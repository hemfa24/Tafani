# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    purchase_warehouse_id = fields.Many2one('stock.warehouse',string="Purchase Warehouse" ,store = True , related ='product_tmpl_id.purchase_warehouse_id' )
