# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SelectProductsADJ(models.TransientModel):

    _name = 'select.products.adj'
    _description = 'Select Products'

    product_ids = fields.Many2many('product.product', string='Products')
    flag_order = fields.Char('Flag Order')

    def select_products(self):
        if self.flag_order == 'adj_temp':
            order_id = self.env['inventory.adjustment.template.new'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['inventory.adjustment.template.new.line'].create({
                    'product_id_new': product.id,
                    'location_id_new': order_id.location_id.id,
                    'inventory_id':order_id.id,
                   
                })
        
