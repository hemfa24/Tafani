# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models, api
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_display_sale_btn = fields.Boolean(string="Enable sale order")
    select_order_state = fields.Selection([('quotation', 'Quotation'), ('confirm', 'Sale Order')], string="Select Order State", default="quotation")

    @api.onchange('sh_display_sale_btn')
    def _onchange_sh_display_sale_btn(self):
        stock_app = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'sale_management')], limit=1)
        if self.sh_display_sale_btn:
            if stock_app.state != 'installed':
                self.sh_display_sale_btn = False
                raise UserError('Sale Management Module not installed ! Please install Sale module first.')
