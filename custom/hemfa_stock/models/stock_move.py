# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    product_uom_id = fields.Many2one(related='product_id.uom_id' ,store=True)
    product_uom_po_id = fields.Many2one(related='product_id.uom_po_id',store=True)

    product_uom = fields.Many2one('uom.uom', string='Unit of Measure' )
