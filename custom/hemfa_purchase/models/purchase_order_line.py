# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_uom_id = fields.Many2one(related='product_id.uom_id')
    product_uom_po_id = fields.Many2one(related='product_id.uom_po_id')

    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
