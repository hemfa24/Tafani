# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_product()
        result['search_params']['fields'].extend(["type", "qty_available"])
        return result

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.sh_display_stock:
            if 'stock.quant' not in result:
                result.append('stock.quant')
            if 'stock.warehouse' not in result:
                result.append('stock.warehouse')
            if 'stock.location' not in result:
                result.append('stock.location')
            if 'stock.picking.type' not in result:
                result.append('stock.picking.type')
        return result

    def _loader_params_stock_quant(self):
        return {'search_params': {'domain': [("location_id.usage", "in", ["internal"])], 'fields': []}}

    def _get_pos_ui_stock_quant(self, params):
        return self.env['stock.quant'].search_read(**params['search_params'])

    def _loader_params_stock_warehouse(self):
        return {'search_params': {'domain': [], 'fields': []}}

    def _get_pos_ui_stock_warehouse(self, params):
        return self.env['stock.warehouse'].search_read(**params['search_params'])

    def _loader_params_stock_location(self):
        return {'search_params': {'domain': [], 'fields': []}}

    def _get_pos_ui_stock_location(self, params):
        return self.env['stock.location'].search_read(**params['search_params'])

    def _loader_params_stock_picking_type(self):
        return {'search_params': {'domain': [], 'fields': []}}

    def _get_pos_ui_stock_picking_type(self, params):
        return self.env['stock.picking.type'].search_read(**params['search_params'])
