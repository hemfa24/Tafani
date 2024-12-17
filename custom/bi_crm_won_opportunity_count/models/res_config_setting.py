# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    opportunity_count = fields.Boolean(string="Opportunity count")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['opportunity_count'] = bool(
            self.env['ir.config_parameter'].sudo().get_param('bi_crm_won_opportunity_count.opportunity_count', default=0))
        return res

    @api.model
    def set_values(self):
        count_opportunity = self.env['ir.config_parameter'].sudo().set_param('bi_crm_won_opportunity_count.opportunity_count', self.opportunity_count)
        super(ResConfigSettings, self).set_values()


    