from odoo import models, fields

class AutoActivityConfig(models.Model):
    _name = 'auto.activity.config'
    _description = 'Auto Activity Configuration'

    name = fields.Char(string='Name', required=True)
    auto_activity = fields.Boolean(string='Auto Activity')
    auto_activity_amount = fields.Integer(string='Auto Activity Amount')
    auto_activity_unit = fields.Selection([('days', 'Days'), ('minutes', 'Minutes')], string='Auto Activity Unit', default='days')
    auto_activity_type = fields.Many2one('mail.activity.type', string='Activity Type')
    auto_activity_user_ids = fields.Many2many('res.users', string='Activity Users')
