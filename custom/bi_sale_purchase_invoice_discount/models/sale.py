# -*- coding: utf-8 -*-
################################################################################
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo.osv import osv
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools.misc import formatLang

class sale_order(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    discount_anlytic_line_id = fields.Many2one('account.analytic.line','Discount Line')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"  

             
class sale_order(models.Model):
    _inherit = 'sale.order'
      
    @api.model_create_multi
    def create(self, vals_list):
        res = super(sale_order,self).create(vals_list)
        for vals in vals_list:
            discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
            discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
            discount_type_obj = self.env['discount.type']
            if vals.get('discount_type_id') == discount_type_percent :
                brw_type = discount_type_obj.browse(discount_type_percent).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s . \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                        (brw_type , brw_type))
            if vals.get('discount_type_id') == discount_type_fixed :
                brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                        (brw_type ,brw_type ))
        return res
    
    
    def write(self, vals):
        discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        discount_type_obj = self.env['discount.type']
        if vals.get('discount_type_id') == discount_type_percent:
            brw_type = discount_type_obj.browse(discount_type_percent).discount_value
            if brw_type > 0.0:
                if vals.get('discount_value',0.00) > brw_type:
                    raise UserError(
                _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                    (brw_type , brw_type))
        if vals.get('discount_value'):
            if self.discount_type_id.id == discount_type_percent:
                brw_type = discount_type_obj.browse(discount_type_percent).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value') > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type') % \
                        (brw_type , brw_type))
            
            elif self.discount_type_id.id == discount_type_fixed:
                brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
                if brw_type > 0.0:
                    if vals.get('discount_value',0.00) > brw_type:
                        raise UserError(
                    _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                        (brw_type ,brw_type ))
        if vals.get('discount_type_id') == discount_type_fixed:
            brw_type = discount_type_obj.browse(discount_type_fixed).discount_value
            if brw_type > 0.0:
                if vals.get('discount_value',0.00) > brw_type:
                    raise UserError(
                _('You can not set Discount Value more then %s. \n Maximum Discount value is %s \n Set maximum value Purchase-> Configuration-> Discount Type' ) % \
                    (brw_type ,brw_type ))
        res = super(sale_order, self).write(vals)
        return res
    
    @api.onchange('apply_discount')
    def onchange_apply_discount(self):
        if self.apply_discount:
            account_search = self.env['account.account'].search([('discount_account', '=', True),('account_type','=','income')])
            if account_search:
                self.discount_account = account_search[0].id
    
    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total','discount_value', 'discount_type_id', 'apply_discount')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            order.amount_untaxed = sum(order_lines.mapped('price_subtotal'))
            order.amount_total = sum(order_lines.mapped('price_total'))
            order.amount_tax = sum(order_lines.mapped('price_tax'))
            if order.apply_discount == True:
                if order.discount_type_id.name == 'Fixed':
                    new_amount_untaxed = order.amount_untaxed - order.discount_value
                else:
                    new_amount_untaxed = order.amount_after_discount
                order.update({
                    'amount_untaxed': new_amount_untaxed,
                    'amount_tax': order.amount_tax,
                    'amount_total': order.amount_after_discount + order.amount_tax,
                })
            else:
                order.update({
                    'amount_untaxed': order.amount_untaxed,
                    'amount_tax': order.amount_tax,
                    'amount_total': order.amount_untaxed + order.amount_tax,
                })

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed','discount_value', 'discount_type_id', 'apply_discount')
    def _compute_tax_totals(self):

        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id,
            )
            discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        
            discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
            res = self._compute_amount_after_discount()
            if order.apply_discount == True:
                order.discount_value = order.discount_value
            else:
                order.discount_value = 0.0
            if order.discount_type_id.id == discount_type_fixed:

                if tax_totals.get('amount_untaxed'):
                    tax_totals['amount_untaxed'] = tax_totals['amount_untaxed'] - order.discount_value
                if tax_totals.get('amount_total'):
                    tax_totals['amount_total'] = tax_totals['amount_untaxed'] + order.amount_tax
                if tax_totals.get('formatted_amount_total'):
                    format_tax_total = tax_totals['amount_untaxed'] + order.amount_tax
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
                                    'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - order.discount_value
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
                                'amount' : subtotals[_tax]['amount'] - order.discount_value
                            })
                        if subtotals[_tax].get('formatted_amount'):
                            format_total = subtotals[_tax]['amount']
                            tax_totals.get('subtotals', {})[_tax].update({
                                'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                            })
                order.tax_totals = tax_totals
            
            elif order.discount_type_id.id == discount_type_percent:
                if tax_totals.get('amount_untaxed'):
                    tax_totals['amount_untaxed'] = res
                if tax_totals.get('amount_total'):
                    tax_totals['amount_total'] = tax_totals['amount_untaxed'] + order.amount_tax
                if tax_totals.get('formatted_amount_total'):
                    format_tax_total = tax_totals['amount_untaxed'] + order.amount_tax
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
                                    'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - order.amount_after_discount
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
                                'amount' : order.amount_after_discount
                            })
                        if subtotals[_tax].get('formatted_amount'):
                            format_total = subtotals[_tax]['amount']
                            tax_totals.get('subtotals', {})[_tax].update({
                                'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
                            })
                order.tax_totals = tax_totals
            else:
                order.tax_totals = tax_totals

    @api.depends('discount_value', 'order_line.price_total','discount_type_id')
    def _compute_amount_after_discount(self):
        res=0.0
        discount = 0.0
        amount_untaxed = 0.0
        count_sale_total = 0.0
        discount_type_percent = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_percent_id')
        
        discount_type_fixed = self.env['ir.model.data']._xmlid_to_res_id('bi_sale_purchase_invoice_discount.discount_type_fixed_id')
        for self_obj in self:
            for line in self_obj.order_line:
                amount_untaxed += line.price_subtotal
            if self_obj.discount_type_id.id == discount_type_fixed:
                discount = amount_untaxed - self_obj.discount_value
                self_obj.amount_after_discount = discount
                res = self_obj.amount_after_discount
            elif self_obj.discount_type_id.id == discount_type_percent:
                discount_percent = amount_untaxed * ((self_obj.discount_value or 0.0) / 100.0)
                discount = amount_untaxed - discount_percent
                self_obj.amount_after_discount = discount
                res = self_obj.amount_after_discount
            else:
                self_obj.amount_after_discount = self_obj.amount_untaxed
            self_obj.count_sale_total = sum(self_obj.order_line.mapped('price_subtotal'))
            return res
     
    
    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()
        invoice_vals.update({
                'discount_type_id' : self.discount_type_id.id,
                'discount_value' : self.discount_value,
                'amount_after_discount' : self.amount_after_discount,
                'out_discount_account' : self.discount_account.id,
                'apply_discount' : self.apply_discount,
            })
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(sale_order,self)._create_invoices(grouped=grouped, final=final,date=date)
        res.update({'discount_type_id' : self.discount_type_id.id,
                'discount_value' : self.discount_value,
                'amount_after_discount' : self.amount_after_discount,
                'out_discount_account' : self.discount_account.id,
                'apply_discount' : self.apply_discount,})

        return res

    apply_discount = fields.Boolean('Apply Discount')
    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Sale Discount')
    discount_account = fields.Many2one('account.account', 'Discount Account')
    amount_after_discount = fields.Monetary('Amount After Discount' , store=True, readonly=True , compute = '_compute_amount_after_discount')
    count_sale_total = fields.Monetary('Sale Total',compute_sudo='_compute_amount_after_discount')
