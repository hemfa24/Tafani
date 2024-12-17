# -*- coding: utf-8 -*-

from odoo import models, fields, api

class resPartner(models.Model):
    _inherit = 'res.partner'

    is_sale_order_payment = fields.Boolean('Sale Order Payment')
    is_purchase_order_payment = fields.Boolean('Purchase Order Payment')

    def action_view_sale_order(self):
        return