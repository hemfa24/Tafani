# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class PosConfg(models.Model):
    _inherit = 'pos.config'

    sh_is_enable_quick_order = fields.Boolean(string="Enable Quick Pos Order")
    sh_is_enable_quick_invoice = fields.Boolean(
        string="Want to Create invoice ?")
    sh_quick_customer = fields.Many2one('res.partner', string="Customer")
    sh_is_quick_payment_method = fields.Many2one(
        'pos.payment.method', string="Payment Method")
