from odoo import models, fields, api
from datetime import timedelta

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    auto_activity = fields.Boolean(string='Auto Activity')
    auto_activity_amount = fields.Integer(string='Auto Activity Amount')
    auto_activity_unit = fields.Selection([('days', 'Days'), ('minutes', 'Minutes')], string='Auto Activity Unit', default='days')
    auto_activity_type_ids = fields.Many2many('mail.activity.type', string='Activity Types')
    auto_activity_user_ids = fields.Many2many('res.users', string='Activity Users')
    cron_id = fields.Many2one('ir.cron', string='Scheduled Action', readonly=True)

    @api.model
    def create(self, vals):
        stage = super(CrmStage, self).create(vals)
        if stage.auto_activity:
            stage._create_or_update_cron()
        return stage

    def write(self, vals):
        res = super(CrmStage, self).write(vals)
        for stage in self:
            if 'auto_activity' in vals or 'auto_activity_amount' in vals or 'auto_activity_unit' in vals:
                if stage.auto_activity:
                    stage._create_or_update_cron()
                elif stage.cron_id:
                    stage.cron_id.unlink()
        return res

    def unlink(self):
        for stage in self:
            if stage.cron_id:
                stage.cron_id.unlink()
        return super(CrmStage, self).unlink()

    def _create_or_update_cron(self):
        for stage in self:
            delta = timedelta(days=stage.auto_activity_amount) if stage.auto_activity_unit == 'days' else timedelta(minutes=stage.auto_activity_amount)
            interval_number = stage.auto_activity_amount
            interval_type = stage.auto_activity_unit
            cron_name = f'Auto Activity Scheduler for Stage {stage.name}'

            if stage.cron_id:
                stage.cron_id.write({
                    'name': cron_name,
                    'interval_number': interval_number,
                    'interval_type': interval_type,
                    'code': f"model._cron_create_auto_activities({stage.id})",
                })
            else:
                cron = self.env['ir.cron'].create({
                    'name': cron_name,
                    'model_id': self.env.ref('crm.model_crm_stage').id,
                    'state': 'code',
                    'code': f"model._cron_create_auto_activities({stage.id})",
                    'interval_number': interval_number,
                    'interval_type': interval_type,
                    'numbercall': -1,
                    'active': True,
                })
                stage.cron_id = cron

    @api.model
    def _cron_create_auto_activities(self, stage_id):
        stage = self.browse(stage_id)
        delta = timedelta(days=stage.auto_activity_amount) if stage.auto_activity_unit == 'days' else timedelta(minutes=stage.auto_activity_amount)
        opportunities = self.env['crm.lead'].search([
            ('stage_id', '=', stage.id),
            ('create_date', '<=', fields.Datetime.now() - delta)
        ])
        for opportunity in opportunities:
            for activity_type in stage.auto_activity_type_ids:
                existing_activities = self.env['mail.activity'].search([
                    ('res_model', '=', 'crm.lead'),
                    ('res_id', '=', opportunity.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('user_id', 'in', stage.auto_activity_user_ids.ids),
                ])
                if not existing_activities:
                    for user in stage.auto_activity_user_ids:
                        self.env['mail.activity'].create({
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
                            'res_id': opportunity.id,
                            'activity_type_id': activity_type.id,
                            'summary': f'Opportunity is still in stage "{stage.name}" for {stage.auto_activity_amount} {stage.auto_activity_unit}',
                            'note': f'Please check the opportunity. It has been in the stage "{stage.name}" for {stage.auto_activity_amount} {stage.auto_activity_unit}.',
                            'user_id': user.id,
                            'date_deadline': fields.Date.today(),
                        })
