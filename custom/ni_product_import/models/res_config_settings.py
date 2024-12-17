# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_gen_variant = fields.Boolean("Auto generate variant", default=True, help="Auto generate variant.")
    
    
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        
        self.env['ir.config_parameter'].set_param('ni_prod_import.auto_gen_variant', self.auto_gen_variant)
        
        return res
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        
        auto_gen_variant = self.env['ir.config_parameter'].sudo().get_param('ni_prod_import.auto_gen_variant')
        res.update(auto_gen_variant = auto_gen_variant)
        return res