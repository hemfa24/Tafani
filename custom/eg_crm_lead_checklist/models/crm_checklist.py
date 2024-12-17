from odoo import fields, models, api, _


class CrmChecklist(models.Model):
    _name = 'crm.checklist'

    name = fields.Char(string='Name', help='Lead Progress Stages')
    lead_id = fields.Many2one(comodel_name='crm.lead')
