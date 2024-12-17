# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('stage_id')
    def _onchange_stage_id_ach(self):
        for rec in self:
            if rec.stage_id.mail_template_id:
                try:
                    email_values = {
                        'auto_delete': True,
                        'message_type': 'comment',
                        'is_notification': True,
                    }
                    mail_id = rec.stage_id.mail_template_id.send_mail(rec._origin.id, force_send=False, raise_exception=True, email_values=email_values)
                except:
                    print('Not send')