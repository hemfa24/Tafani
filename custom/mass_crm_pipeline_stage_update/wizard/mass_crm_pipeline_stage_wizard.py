# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError  


class CustomMassCrmStageWizard(models.TransientModel):
    _name = 'custom.mass.crm.stage.wizard'
    _description = "Mass CRM Pipeline Stage Update"


    def _custom_get_team(self):
        stage = self.env['crm.lead'].browse(self._context.get('active_ids'))
        team_id =  stage.mapped('team_id')
        return team_id


    team_id = fields.Many2one(
        'crm.team',
        string="Sales Team",
        default=_custom_get_team,
        readonly=True,
        required=True,
    )


    def custom_update_stage_crm(self):
        lead_ids = self.env['crm.lead'].browse(self._context.get('active_ids'))
        team_id =  lead_ids.mapped('team_id')
        if len(team_id) > 1:
            raise UserError("For selected record(s) sales team must be same.")
        for stage in lead_ids:
            stage.stage_id = self.stage_id.id
        action = self.with_context(active_id=self.team_id.id).env['ir.actions.actions']._for_xml_id(
                'crm.crm_lead_action_pipeline')
        action['domain'] = [('id', 'in', lead_ids.ids)]
        return action


    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        required=True,
        domain="['|',('team_id','=',team_id),('team_id','=',False)]"
    )