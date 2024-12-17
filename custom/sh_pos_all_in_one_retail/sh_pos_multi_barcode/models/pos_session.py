# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_product()
        result['search_params']['fields'].append('barcode_line_ids')
        return result

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['product_by_barcode'] = {
            data['id']: data for data in loaded_data['product.template.barcode']}
        loaded_data['barcode_by_name'] = {
            data['name']: data for data in loaded_data['product.template.barcode']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'product.template.barcode' not in result:
            result.append('product.template.barcode')
        return result

    def _loader_params_product_template_barcode(self):
        return {'search_params': {'domain': [('available_item','=','t'), ('product_id.active','=', True)], 'fields': ['create_date', 'name', 'product_id', 'unit','price_lst','price', 'available_item', 'negative_qty_price']}}

    def _get_pos_ui_product_template_barcode(self, params):
        return self.env['product.template.barcode'].search_read(**params['search_params'])
