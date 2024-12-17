 # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    custom_number = fields.Char(
        string="Number",
        copy=False,
        readonly=True
    )
    
    # @api.model
    # def create(self, vals): 
    #     vals['custom_number'] = self.env['ir.sequence'].next_by_code('crm.lead')
    #     return super(CrmLead,self).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list: 
            vals['custom_number'] = self.env['ir.sequence'].next_by_code('crm.lead')
        return super(CrmLead,self).create(vals_list)