# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        result = super(PosSession,self)._loader_params_res_company()
        result['search_params']['fields'].extend(['street','street2','city','state_id','vat'])
        return result
    
    def _loader_params_product_product(self):
        result = super(PosSession,self)._loader_params_product_product()
        result['search_params']['fields'].extend(['name','name_arabic'])
        return result