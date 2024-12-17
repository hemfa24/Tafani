# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
import json


class sale_order(models.Model):
    _inherit = 'sale.order'

    # @api.constrains('discount_amount')
    # def check_discount_amount(self):
    #     for rec in self:
    #         if rec.discount_method == 'fix':
    #             line_dis = rec.discount_amount / len(rec.order_line)
    #             if rec.discount_amount > line_dis:
    #                 raise ValidationError(_("Discount Must be less then Unit Price."))
    #         if rec.discount_method == 'per':
    #             if rec.discount_amount > 100:
    #                 raise ValidationError(_("Discount Must be less then 100%."))

    # @api.depends('discount_method', 'discount_amount')
    # def _comupte_discount_amt(self):
    #     for rec in self:
    #         for line in rec.order_line:
    #             line._compute_amount()
    #         line_count = 0
    #         line_count = len(rec.order_line)
    #         dis_amount_to = 0
    #         line_dis = 0
    #         if line_count > 0:
    #             if rec.discount_method == 'fix':
    #                 dis_amount_to = rec.discount_amount
    #             elif rec.discount_method == 'per':
    #                 dis_amount_to = ((rec.discount_amount * rec.amount_untaxed) / 100.0)

    #         if dis_amount_to >= 0 and line_count > 0:
    #             line_dis = dis_amount_to / line_count
    #             rec.ine_save_dis_amount = line_dis
    #             rec.update({
    #                 'discount_amt': dis_amount_to
    #             })
    #             for line in rec.order_line:
    #                 val_price = line.price_subtotal
    #                 line.price_subtotal = val_price - line_dis
    #                 line.price_total = line.price_subtotal

    @api.depends('discount_method', 'discount_amount', 'order_line.product_uom_qty', 'order_line.price_unit')
    def _comupte_discount_amt(self):
        for rec in self:
            if rec.discount_type == 'global':
                line_total_amnt = sum(rec.order_line.mapped('subtotal_before_disc'))
                if rec.discount_method == 'fix':
                    for line in rec.order_line:
                        line = line.with_context(is_from_orderline_discount=True)
                        # line._compute_price_unit()
                        if line_total_amnt:
                            line.price_subtotal = line.subtotal_before_disc - (
                                    line.product_uom_qty * line.unit_price_before_discount / line_total_amnt) * rec.discount_amount
                    rec.discount_amt = rec.discount_amount
                elif rec.discount_method == 'per':
                    sum_original_line_price_subtotal = 0.0
                    for line in rec.order_line:
                        # line._compute_price_unit()
                        sum_original_line_price_subtotal += line.subtotal_before_disc
                        line.price_subtotal = line.subtotal_before_disc - (
                                (line.product_uom_qty * line.unit_price_before_discount * rec.discount_amount) / 100.00)
                    rec.discount_amt = (sum_original_line_price_subtotal * rec.discount_amount) / 100.00

        # self._amount_all()

    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()

        invoice_vals.update({
            'discount_method': self.discount_method,
            'discount_amt': self.discount_amt,
            'discount_amount': self.discount_amount,
            'discount_type': self.discount_type,
            'discount_amt_line': self.discount_amt_line,
            # 'amount_untaxed' : self.amount_untaxed - self.discount_amt,
            # 'amount_total': self.amount_untaxed - self.discount_amt,
        })
        return invoice_vals

    def action_create_invoice(self):
        res = super(sale_order, self).action_create_invoice()
        res.update({'discount_type': self.discount_type})
        invoice_vals = []
        # line = res.invoice_line_ids.filtered(lambda x: x.id)
        # for line in res.invoice_line_ids:
        #     line.update({'discount_balance': self.ine_save_dis_amount
        #     })

        return res

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], string='Discount Method',
                                       default='fix')
    discount_amount = fields.Float('Discount Amount', default=0.0)
    discount_amt = fields.Float(store=True, string='- Discount', readonly=True, compute='_comupte_discount_amt')
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Applies to',
                                     default='global')
    discount_amt_line = fields.Float(string='- Line Discount', digits='Line Discount', store=True,
                                     readonly=True)  # compute='_amount_all',

    config_tax = fields.Monetary(string="total disc tax", store=True)  # compute="_amount_all",
    report_total = fields.Float("Report Untaxed Amount", readonly=True)  # compute="_calculate_report_total",
    untax_test_amount = fields.Float(string="total untax amount for line", store=True)  # compute="_calculate_discount"
    line_total_amount = fields.Float(string="total  amount for line", store=True)  # compute="_calculate_discount",
    ine_save_dis_amount = fields.Float(string="amount for line", store=True)

    @api.onchange('discount_type')
    def _onchange_cust_discount_type(self):
        for order in self:
            if order.discount_type == 'global':
                order.order_line.write({
                    'is_make_lock_price_unit': False
                })

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'discount_amount')
    def _compute_tax_totals(self):
        res_config = self.env.company
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id,
            )
            if order.discount_type == 'global':
                res = order.discount_amt  # self._calculate_discount()
            else:
                res = 0
            if tax_totals.get('amount_untaxed'):
                tax_totals['amount_untaxed'] = tax_totals['amount_untaxed'] - res

            if tax_totals.get('formatted_amount_total'):
                format_tax_total = tax_totals['amount_untaxed'] + order.amount_tax
                tax_totals['formatted_amount_total'] = formatLang(self.env, format_tax_total,
                                                                  currency_obj=self.currency_id)

            if tax_totals.get('formatted_amount_untaxed'):
                format_total = tax_totals['amount_untaxed']
                tax_totals['formatted_amount_untaxed'] = formatLang(self.env, format_total,
                                                                    currency_obj=self.currency_id)

            groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
            if bool(groups_by_subtotal):
                _untax_amount = groups_by_subtotal.get('Untaxed Amount', [])
                if bool(_untax_amount):
                    if res_config.tax_discount_policy == 'tax':
                        for _tax in range(len(_untax_amount)):

                            if _untax_amount[_tax].get('tax_group_base_amount'):
                                tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                    'tax_group_base_amount': _untax_amount[_tax]['tax_group_base_amount'] - res
                                })
                            if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
                                tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                    'formatted_tax_group_base_amount': formatLang(self.env, format_total,
                                                                                  currency_obj=self.currency_id)
                                })
                    else:
                        for _tax in range(len(_untax_amount)):
                            if order.discount_type == 'global':
                                if _untax_amount[_tax].get('tax_group_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_amount': self.config_tax
                                    })

                                if _untax_amount[_tax].get('tax_group_base_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_base_amount': _untax_amount[_tax]['tax_group_base_amount'] - res
                                    })
                                if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                    format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_base_amount': formatLang(self.env, format_total,
                                                                                      currency_obj=self.currency_id)
                                    })

                                if _untax_amount[_tax].get('formatted_tax_group_amount'):
                                    format_total = self.config_tax
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_amount': formatLang(self.env, format_total,
                                                                                 currency_obj=self.currency_id)
                                    })

                            else:
                                if _untax_amount[_tax].get('tax_group_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_amount': order.amount_tax
                                    })
                                if _untax_amount[_tax].get('tax_group_base_amount'):
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'tax_group_base_amount': _untax_amount[_tax]['tax_group_base_amount'] - res
                                    })

                                if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
                                    format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_base_amount': formatLang(self.env, format_total,
                                                                                      currency_obj=self.currency_id)
                                    })

                                if _untax_amount[_tax].get('formatted_tax_group_amount'):
                                    format_total = order.amount_tax
                                    tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
                                        'formatted_tax_group_amount': formatLang(self.env, format_total,
                                                                                 currency_obj=self.currency_id)
                                    })

            subtotals = tax_totals.get('subtotals', {})
            if bool(subtotals):
                for _tax in range(len(subtotals)):
                    if subtotals[_tax].get('amount'):
                        tax_totals.get('subtotals', {})[_tax].update({
                            'amount': subtotals[_tax]['amount'] - res
                        })
                    if subtotals[_tax].get('amount_tax'):
                        tax_totals.get('subtotals', {})[_tax].update({
                            'amount_tax': res
                        })
                    if subtotals[_tax].get('formatted_amount'):
                        format_total = subtotals[_tax]['amount']
                        tax_totals.get('subtotals', {})[_tax].update({
                            'formatted_amount': formatLang(self.env, format_total, currency_obj=self.currency_id)
                        })

            order.tax_totals = tax_totals

    #

    @api.constrains('discount_amount', 'discount_method')
    def _check_discount_amount(self):
        for rec in self:
            if rec.discount_method == 'fix':
                if rec.discount_amount > rec.amount_total:
                    raise UserError(_("Given discount is more than the actual amount of sales order"))
                elif rec.discount_amount > self.env.user.fixed_limit:
                    raise UserError(
                        _("Given discount is more than the allowed discount. Maximum allowed discount is %s" % (
                            self.env.user.fixed_limit)))
            elif rec.discount_method == 'per':
                if rec.discount_amount > self.env.user.percentage_limit:
                    raise UserError(
                        _("Given discount is more than the allowed discount. Maximum allowed discount is %s" % (
                            self.env.user.percentage_limit)))


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    discount_method = fields.Selection(
        [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')
    subtotal_before_disc = fields.Float(
        string='Subtotal before Discount',
        compute='_compute_amount',
        store=True
    )
    unit_price_before_discount = fields.Float(
        string='Unit Price before Discount',
        compute='_compute_unit_price_before_disc',
        store=True,
    )
    is_make_lock_price_unit = fields.Boolean(
        string='Lock Price Unit',
    )

    def action_lock_price_unit(self):
        for rec in self:
            rec.is_make_lock_price_unit = True
            rec.discount_amount = 0.0

    def action_edit_price_unit(self):
        for rec in self:
            rec.is_make_lock_price_unit = False

    @api.depends('is_make_lock_price_unit', 'price_unit')
    def _compute_unit_price_before_disc(self):
        for rec in self:
            if not rec.is_make_lock_price_unit:
                rec.unit_price_before_discount = rec.price_unit

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            print ("#############line.order_id.discount_type",line.order_id.discount_type)
            if line.is_make_lock_price_unit or (line.order_id.discount_type == 'global' and line.price_unit > 0.0):
                self -= line
                continue
        super(sale_order_line, self)._compute_price_unit()


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        super(sale_order_line, self)._compute_amount()
        for line in self:
            line.subtotal_before_disc = line.price_subtotal

    @api.constrains('discount_amount')
    def check_discount_amount(self):
        for rec in self:
            if rec.order_id.discount_type == 'line':
                if rec.discount_amount < 0:
                    raise ValidationError(_("Discount Must be Greater than Zero."))
                if rec.discount_method == 'fix':
                    if rec.price_unit < 0.0:
                        raise ValidationError(_("Discount Must be less than Unit Price."))
                if rec.discount_method == 'per':
                    if rec.discount_amount > 100:
                        raise ValidationError(_("Discount Must be less than 100%."))

    @api.depends('discount_method', 'discount_amount', 'product_id')
    @api.onchange('discount_amount')
    def onchange_discount_metho(self):
        for rec in self:
            # rec._compute_price_unit()
            if rec.order_id.discount_type == 'line':
                if rec.discount_method == 'fix':
                    if rec.discount_amount > 0.0:
                        val_price = rec.unit_price_before_discount
                        # rec.price_unit = val_price - rec.discount_amount
                        rec.write({
                            'price_unit' : val_price - rec.discount_amount
                        })
                    else:
                        # rec.price_unit = rec.unit_price_before_discount
                        rec.write({
                            'price_unit': rec.unit_price_before_discount
                        })
                if rec.discount_method == 'per':
                    if rec.discount_amount > 0.0:
                        val_price = rec.unit_price_before_discount
                        val_dis = ((rec.discount_amount * rec.unit_price_before_discount) / 100.0)
                        # rec.price_unit = val_price - val_dis
                        rec.write({
                            'price_unit': val_price - val_dis
                        })
                    else:
                        # rec.price_unit = rec.unit_price_before_discount
                        rec.write({
                            'price_unit': rec.unit_price_before_discount
                        })

    def _prepare_invoice_line(self, **optional_values):
        res = super(sale_order_line, self)._prepare_invoice_line(**optional_values)
        res.update({'discount': self.discount,
                    'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount,
                    'discount_amt': self.discount_amt,
                    'is_make_lock_price_unit': self.is_make_lock_price_unit,
                    'unit_price_before_discount': self.unit_price_before_discount})
        return res

    class ResCompany(models.Model):
        _inherit = 'res.company'

        tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                               default_model='sale.order', default='tax')

        sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',
                                          domain=[('user_type_id.name', '=', 'Expenses'),
                                                  ('discount_account', '=', True)])
        purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',
                                              domain=[('user_type_id.name', '=', 'Income'),
                                                      ('discount_account', '=', True)])

        def _valid_field_parameter(self, field, name):
            return name == 'default_model' or super()._valid_field_parameter(field, name)

    class ResConfigSettings(models.TransientModel):
        _inherit = 'res.config.settings'

        tax_discount_policy = fields.Selection(readonly=False, related='company_id.tax_discount_policy',
                                               string='Discount Applies On', default_model='sale.order')
        sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',
                                          domain=[('user_type_id.name', '=', 'Expenses'),
                                                  ('discount_account', '=', True)],
                                          related="company_id.sale_account_id")
        purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',
                                              domain=[('user_type_id.name', '=', 'Income'),
                                                      ('discount_account', '=', True)],
                                              related="company_id.purchase_account_id")
