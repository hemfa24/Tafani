from collections import defaultdict
from itertools import groupby
import logging
from datetime import timedelta
from functools import partial
import psycopg2
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

#############################################################################################################
#############################################################################################################


class PosSessions(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super(PosSessions, self)._pos_data_process(loaded_data)
        products = loaded_data['product.product']

        for product in products:
            prod_list = []
            for option in product['pos_multi_barcode_option']:
                for option_item in loaded_data['pos.multi.barcode.options']:
                    prod_list.append(option_item)
            product['pos_multi_barcode_option'] = prod_list

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'pos.multi.barcode.options'
        result.append(new_model)
        return result

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('pos_multi_barcode_option')
        return result

    def _get_pos_ui_pos_multi_barcode_options(self, params):
        return self.env['pos.multi.barcode.options'].with_context(
            **params['context']).search_read(**params['search_params'])

    def _loader_params_pos_multi_barcode_options(self):
        return {
            'search_params': {
                'fields': [
                    'name',
                    'product_id',
                    'qty',
                    'price',
                    'unit',
                    'price_lst'
                ],
            },
            'context': {'display_default_code': False},
        }

#############################################################################################################
#############################################################################################################
