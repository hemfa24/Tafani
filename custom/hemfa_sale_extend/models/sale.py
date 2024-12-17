# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains('pricelist_id', 'currency_id')
    def _constrains_display_accounts(self):
        for rec in self:
            if rec.currency_id.id != rec.company_id.currency_id.id:
                if rec.sale_manual_currency_rate == 0.0 or not rec.sale_manual_currency_rate_active:
                    raise UserError(_(
                        'Please Apply Manual Exchange and enter exchange currency Rate!!!'
                    ))

    @api.onchange('pricelist_id', 'currency_id')
    def onchange_method(self):
        for rec in self:
            if rec.currency_id.id != rec.company_id.currency_id.id:
                rec.sale_manual_currency_rate_active = True
            else:
                rec.sale_manual_currency_rate_active = False
