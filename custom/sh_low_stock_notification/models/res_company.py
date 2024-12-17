# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_quantity_check = fields.Selection([('global', 'Global'), ('individual', 'Individual'), (
        'order_point', 'Reorder Rules (Order Points)')], default="global",)
    minimum_quantity = fields.Float()
    notify_user_id = fields.Many2one("res.users", "Notify User")
    low_stock_notification = fields.Boolean("Low Stock Notification ?")
    sh_chouse_qty_type = fields.Selection([('on_hand', 'On Hand'), (
        'forcasted', 'Forcasted')], default='on_hand', string='Select Quantity Type ')
