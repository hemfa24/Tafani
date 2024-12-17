# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
#    _inherit = 'account.invoice'
    _inherit = 'account.move'

#    @api.model
#    def _refund_cleanup_lines(self, lines):#NEED TO CHECK
#        result = super(AccountInvoice, self)._refund_cleanup_lines(lines)
#        for i, line in enumerate(lines):
#            for name, field in line._fields.items():
#                if name == 'asset_category_id':
#                    result[i][2][name] = False
#                    break
#        return result

    #@api.multi
#    def action_cancel(self):
    def button_cancel(self):
        res = super(AccountInvoice, self).button_cancel()#action_cancel()
        self.env['account.asset.asset.custom'].sudo().search([('invoice_id', 'in', self.ids)]).write({'active': False})
        return res

    #@api.multi
#    def action_move_create(self):#NEED TO CHECK
#        result = super(AccountInvoice, self).action_move_create()
    #def post(self):
    def _post(self, soft=True):
        # result = super(AccountInvoice, self).post()
#        result = super(AccountInvoice, self).post(soft)
        result = super(AccountInvoice, self)._post(soft=soft)
        for inv in self:
            context = dict(self.env.context)
            # Within the context of an invoice,
            # this default value is for the type of the invoice, not the type of the asset.
            # This has to be cleaned from the context before creating the asset,
            # otherwise it tries to create the asset with the type of the invoice.
            context.pop('default_type', None)
            inv.invoice_line_ids.with_context(context).asset_create()
        return result


class AccountInvoiceLine(models.Model):
#    _inherit = 'account.invoice.line'
    _inherit = 'account.move.line'

    asset_category_id = fields.Many2one('account.asset.category.custom', string='Asset Category')
    asset_start_date = fields.Date(string='Asset Start Date', compute='_get_asset_date', readonly=True, store=True)
    asset_end_date = fields.Date(string='Asset End Date', compute='_get_asset_date', readonly=True, store=True)
    asset_mrr = fields.Float(string='Monthly Recurring Revenue', compute='_get_asset_date', readonly=True, digits=dp.get_precision('Account'), store=True)

#    @api.one
#    @api.depends('asset_category_id', 'invoice_id.date_invoice')
    @api.depends('asset_category_id', 'move_id.invoice_date')
    def _get_asset_date(self):
#        self.asset_mrr = 0
#        self.asset_start_date = False
#        self.asset_end_date = False
#        cat = self.asset_category_id
#        if cat:
#            if cat.method_number == 0 or cat.method_period == 0:
#                raise UserError(_('The number of depreciations or the period length of your asset category cannot be null.'))
#            months = cat.method_number * cat.method_period
##            if self.invoice_id.type in ['out_invoice', 'out_refund']:
#            if self.move_id.type in ['out_invoice', 'out_refund']:
#                self.asset_mrr = self.price_subtotal / months #NEED TO CHECK #self.price_subtotal_signed / months
##            if self.invoice_id.date_invoice:
#            if self.move_id.invoice_date:
#                # start_date = datetime.strptime(str(self.invoice_id.date_invoice), DF).replace(day=1)s
##                start_date = self.invoice_id.date_invoice.replace(day=1)
#                start_date = self.move_id.invoice_date.replace(day=1)
#                end_date = (start_date + relativedelta(months=months, days=-1))
#                self.asset_start_date = start_date.strftime(DF)
#                self.asset_end_date = end_date.strftime(DF)
        for line in self:
            line.asset_mrr = 0
            line.asset_start_date = False
            line.asset_end_date = False
            cat = line.asset_category_id
            if cat:
                if cat.method_number == 0 or cat.method_period == 0:
                    raise UserError(_('The number of depreciations or the period length of your asset category cannot be null.'))
                months = cat.method_number * cat.method_period
#                if line.move_id.type in ['out_invoice', 'out_refund']:
                if line.move_id.move_type in ['out_invoice', 'out_refund']:
                    line.asset_mrr = line.price_subtotal / months #NEED TO CHECK #self.price_subtotal_signed / months
                if line.move_id.invoice_date:
                    start_date = line.move_id.invoice_date.replace(day=1)
                    end_date = (start_date + relativedelta(months=months, days=-1))
                    line.asset_start_date = start_date.strftime(DF)
                    line.asset_end_date = end_date.strftime(DF)

#    @api.one
    def asset_create(self):
        for line in self:
            if line.asset_category_id:
                vals = {
                    'name': line.name,
    #                'code': self.invoice_id.number or False,
                    'code': line.move_id.name or False,
                    'category_id': line.asset_category_id.id,
    #                'value': self.price_subtotal_signed,
#                    'value': line.price_subtotal,#NEED TO CHECK,
                    'value': line.move_id.currency_id._convert(line.price_subtotal, line.move_id.company_id.currency_id, line.move_id.company_id, line.move_id.invoice_date),
    #                'partner_id': self.invoice_id.partner_id.id,
    #                'company_id': self.invoice_id.company_id.id,
    #                'currency_id': self.invoice_id.company_currency_id.id,
    #                'date': self.invoice_id.date_invoice,
    #                'invoice_id': self.invoice_id.id,
                    'partner_id': line.move_id.partner_id.id,
                    'company_id': line.move_id.company_id.id,
                    'currency_id': line.move_id.company_currency_id.id,
                    'date': line.move_id.invoice_date,
                    'invoice_id': line.move_id.id,
                }
                changed_vals = self.env['account.asset.asset.custom'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                print ("YYYYYYYYYvals",vals)
                asset = self.env['account.asset.asset.custom'].create(vals)
                if line.asset_category_id.open_asset:
                    asset.validate()
        return True

    @api.onchange('asset_category_id')
    def onchange_asset_category_id(self):
#        if self.invoice_id.type == 'out_invoice' and self.asset_category_id:
#        if self.move_id.type == 'out_invoice' and self.asset_category_id:
        if self.move_id.move_type == 'out_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id
#        elif self.invoice_id.type == 'in_invoice' and self.asset_category_id:
#        elif self.move_id.type == 'in_invoice' and self.asset_category_id:
        elif self.move_id.move_type == 'in_invoice' and self.asset_category_id:
            self.account_id = self.asset_category_id.account_asset_id.id

#    @api.onchange('uom_id')
    @api.onchange('product_uom_id')
#    def _onchange_uom_id(self):
#        result = super(AccountInvoiceLine, self)._onchange_uom_id()
    def _onchange_uom_id_custom(self):
        self.onchange_asset_category_id()
#        return result

    @api.onchange('product_id')
#    def _onchange_product_id(self):
#        vals = super(AccountInvoiceLine, self)._onchange_product_id()
    def _onchange_product_id_custom(self):
        if self.product_id:
#            if self.invoice_id.type == 'out_invoice':
#            if self.move_id.type == 'out_invoice':
            if self.move_id.move_type == 'out_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id
#            elif self.invoice_id.type == 'in_invoice':
#            elif self.move_id.type == 'in_invoice':
            elif self.move_id.move_type == 'in_invoice':
                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id
#        return vals

#    def _set_additional_fields(self, invoice):#NEED TO CHECK
#        if not self.asset_category_id:
#            if invoice.type == 'out_invoice':
#                self.asset_category_id = self.product_id.product_tmpl_id.deferred_revenue_category_id.id
#            elif invoice.type == 'in_invoice':
#                self.asset_category_id = self.product_id.product_tmpl_id.asset_category_id.id
#            self.onchange_asset_category_id()
#        super(AccountInvoiceLine, self)._set_additional_fields(invoice)

#    def _get_computed_account(self):#get_invoice_line_account
#        return self.product_id.asset_category_id.account_asset_id or super(AccountInvoiceLine, self)._get_computed_account()
    
    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):#_get_computed_account
        return self.product_id.asset_category_id.account_asset_id or super(AccountInvoiceLine, self)._compute_account_id()

#    def get_invoice_line_account(self, type, product, fpos, company):
#        return product.asset_category_id.account_asset_id or super(AccountInvoiceLine, self).get_invoice_line_account(type, product, fpos, company)
