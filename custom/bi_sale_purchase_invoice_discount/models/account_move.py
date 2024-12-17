# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
import time
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from contextlib import ExitStack, contextmanager

class account_account(models.Model):
    _inherit = 'account.account'
    
    discount_account = fields.Boolean('Discount Account')
    
class account_move(models.Model):
    _inherit = 'account.move'

    invoice_line_ids = fields.One2many(  # /!\ invoice_line_ids is just a subset of line_ids.
        'account.move.line',
        'move_id',
        string='Invoice lines',
        copy=False,
        readonly=True,
        domain=[('display_type', 'in', ('product', 'line_section', 'line_note')),('exclude_from_invoice_tab', '=', False)],
        states={'draft': [('readonly', False)]},
    )   


    @api.depends('discount_value','discount_type_id')
    def _compute_amount_after_discount(self):
        discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        res = discount = 0.0
        for self_obj in self:
            if self_obj.discount_type_id.id == discount_type_fixed:
                res = self_obj.discount_value
                self_obj.amount_after_discount = self_obj.amount_untaxed - res
            elif self_obj.discount_type_id.id == discount_type_percent: 
                total = 0.0
                for line in self.invoice_line_ids:
                    if line.exclude_from_invoice_tab == False:
                        total += line.price_unit 
                    res = total * (self_obj.discount_value/ 100)
                    self_obj.amount_after_discount = res
            else:
                res = 0.0  
            if self_obj.invoice_line_ids:
                if self_obj.invoice_line_ids[0].product_id:
                    if "Down payment" in self_obj.invoice_line_ids[0].product_id.name:
                        self_obj.discount_value = 0.0
                        self_obj.apply_discount = False
                    if "Down Payments" in self_obj.invoice_line_ids[0].product_id.name:
                        self_obj.discount_value = 0.0
                        self_obj.apply_discount = False  
            return res 


    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            if self.move_type == 'out_invoice':
                account_search = self.env['account.account'].search([('account_type','=','income'),('discount_account', '=', True)])
                if account_search:
                    self.update( {'out_discount_account':account_search[0].id})
            if self.move_type == 'in_invoice':
                account_search = self.env['account.account'].search([('account_type','=','expense'),('discount_account', '=', True)])
                if account_search:
                    self.update( {'in_discount_account':account_search[0].id})
                
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id','discount_value',
        'amount_after_discount',
        'discount_type_id',)
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice():
                    # === Invoices ===

                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign
            

            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total 
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
        
            res = move._compute_amount_after_discount()
            discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        
            discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')

            final_subtotal = sum(line.price_subtotal for line in move.invoice_line_ids)
            
            if move.apply_discount == True:
                move.discount_value = move.discount_value
            else:
                move.discount_value = 0.0
            
            if move.discount_type_id.id == discount_type_fixed:
                move.amount_after_discount = final_subtotal - move.discount_value
            else:
                discount = final_subtotal  * ((move.discount_value or 0.0) / 100.0)
                move.extra_discount = discount
                move.amount_after_discount = final_subtotal - discount
 
    discount_type_id = fields.Many2one('discount.type', 'Discount Type',)
    discount_value = fields.Float('Discount Value')
    out_discount_account = fields.Many2one('account.account', 'Discount Account')
    in_discount_account = fields.Many2one('account.account', 'Discount Account ')
    amount_after_discount = fields.Monetary('Amount After Discount', store=True, readonly=True, tracking=True,
        compute='_compute_amount')
    apply_discount = fields.Boolean('Apply Discount')
    discount_move_line_id = fields.Many2one('account.move.line','Discount Line')
    purchase_order = fields.Boolean('is a PO',default=False)  
    extra_discount = fields.Monetary(string="Extra Discount")

    def _compute_amount_invoice(self):
        for move in self:
            total_x = 0.0
            for line in self.invoice_line_ids:
                if line.exclude_from_invoice_tab == False:
                    total_x += line.price_subtotal
            move.update({'total_x':total_x})
    
    
    total_x =fields.Float(string="Invoice total",compute="_compute_amount_invoice")                    
    

    @api.model_create_multi
    def create(self, vals_list):
        result = super(account_move,self).create(vals_list)

        for move in result:
            if move.move_type != 'entry' and move.state in 'draft' and move.discount_value > 0 and move.discount_type_id:
            
                discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
                discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')

                if move.discount_type_id.id == discount_type_percent:
                    total = sum(line.price_subtotal for line in move.invoice_line_ids)
                    res_x = total * (move.discount_value/ 100)
                    l = move.line_ids.filtered(lambda s: s.name == 'Discount')
                    if len(l or []) == 0 :
                        
                        discount_vals = { 
                            'account_id': move.out_discount_account.id or move.in_discount_account.id, 
                            'quantity': 1,
                            'price_unit': -res_x,
                            'name': "Discount",
                            'tax_ids': None, 
                            'exclude_from_invoice_tab': True,
                            'display_type':'product',
                        } 
                        move.with_context(check_move_validity=False).write({
                                'invoice_line_ids' : [(0,0,discount_vals)]
                            })
                else:
                    for line in move.invoice_line_ids:
                    
                        l = move.line_ids.filtered(lambda s: s.name == 'Discount')
                        if len(l or []) == 0 :
                            
                           
                            discount_vals = { 
                                'account_id': move.out_discount_account.id or move.in_discount_account.id, 
                                'quantity': 1,
                                'price_unit': -move.discount_value,
                                'name': "Discount",
                                'tax_ids': None, 
                                'exclude_from_invoice_tab': True,
                                'display_type':'product',
                            } 
                            move.with_context(check_move_validity=False).write({
                                    'invoice_line_ids' : [(0,0,discount_vals)]
                                })
        return result


    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id','amount_total', 'amount_untaxed','discount_value'
    )
    def _compute_tax_totals(self):

        res_config= self.env.company
        
        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
                sign = move.direction_sign
                if move.id:
                    # The invoice is stored so we can add the early payment discount lines directly to reduce the
                    # tax amount without touching the untaxed amount.
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,
                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    # In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
                    # we need to simulate them.
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.currency_id,
                            taxes=taxes,
                            price_unit=values['price_subtotal'],
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'],
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))
                tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
                
                discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
                discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')

                if move.apply_discount == True:
                    move.discount_value = move.discount_value
                else:
                    move.discount_value = 0.0
                
                if move.discount_type_id.id == discount_type_fixed:

                    if tax_totals.get('amount_untaxed'):
                        tax_totals['amount_untaxed'] = tax_totals['amount_untaxed'] - move.discount_value
                    if tax_totals.get('formatted_amount_total'):
                        format_tax_total = tax_totals['amount_untaxed'] + move.amount_tax
                        tax_totals['formatted_amount_total'] = formatLang(self.env, format_tax_total, currency_obj=self.currency_id)
                    if tax_totals.get('formatted_amount_untaxed'):
                        format_total = tax_totals['amount_untaxed']
                        tax_totals['formatted_amount_untaxed'] = formatLang(self.env, format_total, currency_obj=self.currency_id)
                    groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
                    if bool(groups_by_subtotal):
                        _untax_amount = groups_by_subtotal.get('Untaxed Amount', [])
                        if bool(_untax_amount):
                            for _tax in range(len(_untax_amount)):
                                if _untax_amount[_tax].get('tax_group_base_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - move.discount_value
                                    })
                                if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                    format_total = _untax_amount[_tax]['tax_group_base_amount']
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                    })
                    subtotals = tax_totals.get('subtotals', {})
                    if bool(subtotals):
                        for _tax in range(len(subtotals)):
                            if subtotals[_tax].get('amount'):
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'amount' : subtotals[_tax]['amount'] - move.discount_value
                                })
                            if subtotals[_tax].get('formatted_amount'):
                                format_total = subtotals[_tax]['amount']
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                })
                    move.update({'amount_untaxed_signed': move.amount_untaxed,
                        'amount_total_signed': move.amount_total})
                    move.tax_totals = tax_totals

                elif move.discount_type_id.id == discount_type_percent:
                    if tax_totals.get('amount_untaxed'):
                        tax_totals['amount_untaxed'] = move.amount_after_discount
                    if tax_totals.get('formatted_amount_total'):
                        format_tax_total = tax_totals['amount_untaxed'] + move.amount_tax
                        tax_totals['formatted_amount_total'] = formatLang(self.env, format_tax_total, currency_obj=self.currency_id)
                    if tax_totals.get('formatted_amount_untaxed'):
                        format_total = tax_totals['amount_untaxed']
                        tax_totals['formatted_amount_untaxed'] = formatLang(self.env, format_total, currency_obj=self.currency_id)
                    groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
                    if bool(groups_by_subtotal):
                        _untax_amount = groups_by_subtotal.get('Untaxed Amount', [])
                        if bool(_untax_amount):
                            for _tax in range(len(_untax_amount)):
                                if _untax_amount[_tax].get('tax_group_base_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - move.amount_after_discount
                                    })
                                if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                    format_total = _untax_amount[_tax]['tax_group_base_amount'] - move.amount_after_discount
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                    })
                    subtotals = tax_totals.get('subtotals', {})
                    if bool(subtotals):
                        for _tax in range(len(subtotals)):
                            if subtotals[_tax].get('amount'):
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'amount' : move.amount_after_discount
                                })
                            if subtotals[_tax].get('formatted_amount'):
                                format_total = subtotals[_tax]['amount']
                                tax_totals.get('subtotals', {})[_tax].update({
                                    'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                                })
                    move.update({'amount_untaxed_signed': move.amount_untaxed,
                        'amount_total_signed': move.amount_total})
                    move.tax_totals = tax_totals
                else:
                    move.tax_totals = tax_totals
            else:
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals = None

    @contextmanager
    def _sync_dynamic_lines(self, container):

        with self._disable_recursion(container, 'skip_invoice_sync') as disabled:
            if disabled:
                yield
                return
            def update_containers():
                # Only invoice-like and journal entries in "auto tax mode" are synced
                tax_container['records'] = container['records'].filtered(lambda m: (m.is_invoice(True) or m.line_ids.tax_ids and not m.tax_cash_basis_origin_move_id))
                invoice_container['records'] = container['records'].filtered(lambda m: m.is_invoice(True))
                misc_container['records'] = container['records'].filtered(lambda m: m.move_type == 'entry' and not m.tax_cash_basis_origin_move_id)

            tax_container, invoice_container, misc_container = ({} for __ in range(3))
            update_containers()
            with ExitStack() as stack:
                stack.enter_context(self._sync_dynamic_line(
                    existing_key_fname='term_key',
                    needed_vals_fname='needed_terms',
                    needed_dirty_fname='needed_terms_dirty',
                    line_type='payment_term',
                    container=invoice_container,
                ))
                stack.enter_context(self._sync_unbalanced_lines(misc_container))
                stack.enter_context(self._sync_rounding_lines(invoice_container))
                stack.enter_context(self._sync_dynamic_line(
                    existing_key_fname='tax_key',
                    needed_vals_fname='line_ids.compute_all_tax',
                    needed_dirty_fname='line_ids.compute_all_tax_dirty',
                    line_type='tax',
                    container=tax_container,
                ))
                stack.enter_context(self._sync_dynamic_line(
                    existing_key_fname='epd_key',
                    needed_vals_fname='line_ids.epd_needed',
                    needed_dirty_fname='line_ids.epd_dirty',
                    line_type='epd',
                    container=invoice_container,
                ))
                stack.enter_context(self._sync_invoice(invoice_container))
                line_container = {'records': self.line_ids}
                

                with self.line_ids._sync_invoice(line_container):
                    yield
                    line_container['records'] = self.line_ids

                    def find_discont_line(line_container):
                        return line_container['records'].filtered(lambda line: line.name == 'Discount')

                    discont_line = find_discont_line(line_container)
                    if discont_line:
                        if self.discount_type_id.name == "Fixed" : 
                            new_debit_value = self.discount_value
                        elif self.discount_type_id.name == "Percent":
                            new_debit_value = self.extra_discount
                        else:
                            new_debit_value = 0.0
                        if self.move_type in ['out_invoice','out_refund','out _receipt'] :
                           discont_line.write({'debit': new_debit_value})
                        elif self.move_type in ['in_invoice','in_refund','in _receipt'] :
                           discont_line.write({'credit': new_debit_value})
                update_containers()


class account_move_line(models.Model):
    _inherit = 'account.move.line' 

    discount_line = fields.Boolean('is a discount line')
    purchase_line = fields.Boolean('is a purchase line',default=False)
    sale_line = fields.Boolean('is a sale line',default=False)
    exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")                


