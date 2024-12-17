from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    checklist_ids = fields.One2many(comodel_name='crm.checklist', string='Check list', inverse_name='lead_id',
                                    store=True)

    progress = fields.Float("Progress", store=True, group_operator="avg",
                            help="Display progress of current task.")

    @api.onchange('checklist_ids')
    def _onchange_checklist(self):
        for rec in self:
            line_ids = self.env['crm.checklist'].search([]).ids
            lines = len(rec.mapped('checklist_ids'))
            if line_ids:
                rec.progress = round((lines / len(line_ids)) * 100)
            else:
                rec.progress = 0

