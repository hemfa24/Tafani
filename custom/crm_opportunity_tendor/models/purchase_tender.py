# -*- coding: utf-8 -*-

from odoo import fields, models, api
    
    
class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    custom_lead_id = fields.Many2one(
        'crm.lead', 
        string='Opportunity',
        copy=False,
        readonly=True,
    )
