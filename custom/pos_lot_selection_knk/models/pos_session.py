# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.osv.expression import OR


class PosSession(models.Model):
    _inherit = 'pos.session'



    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['qty_available', 'packaging_ids'])
        return result

    

    def _pos_ui_models_to_load(self):
    	result = super()._pos_ui_models_to_load()
    	result.append('stock.lot')
    	return result


    def _loader_params_stock_lot(self):
    	return{
    	'search_params': {
    	'domain': [('company_id', '=', self.company_id.id)],
    	'fields': ['id', 'name', 'display_name', 'company_id', 'product_id', 'product_qty'],
    	},

    	}

    def _get_pos_ui_stock_lot(self, params):
    	
    	return self.env['stock.lot'].search_read(**params['search_params'])

    	
