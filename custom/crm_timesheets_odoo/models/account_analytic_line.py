# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    crm_lead_custom_id = fields.Many2one(
        'crm.lead', 
        'CRM Pipeline',
        copy = False
    )
