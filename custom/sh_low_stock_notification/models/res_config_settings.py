# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_quantity_check = fields.Selection(related='company_id.product_quantity_check',
                                              default=lambda self: self.env.company.product_quantity_check, required=True, readonly=False)
    minimum_quantity = fields.Float(related='company_id.minimum_quantity',
                                    default=lambda self: self.env.company.minimum_quantity, readonly=False)
    notify_user_id = fields.Many2one("res.users", "Notify User", related='company_id.notify_user_id',
                                     default=lambda self: self.env.company.notify_user_id, readonly=False)
    low_stock_notification = fields.Boolean(
        "Low Stock Notification ?", related='company_id.low_stock_notification', readonly=False)
    sh_chouse_qty_type = fields.Selection(
        related='company_id.sh_chouse_qty_type', string='Select Quantity Type', readonly=False)
