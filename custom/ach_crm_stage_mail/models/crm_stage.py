# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    mail_template_id = fields.Many2one('mail.template', string="Mail Template")