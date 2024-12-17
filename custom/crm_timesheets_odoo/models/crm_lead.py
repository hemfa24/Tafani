# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class Lead(models.Model):
    _inherit = "crm.lead"

    custom_timesheet_ids = fields.One2many(
        'account.analytic.line', 
        'crm_lead_custom_id', 
        'Timesheets',
        copy = False
    )
    