from odoo import models, fields, api, _
from datetime import datetime


class RequestRejectWizard(models.TransientModel):
    _name = 'request.reject.wizard'
    _description = 'Reject Request'

    reason = fields.Char(string="Refuse Reason")

    def reject_button(self):
        current_id = self.env['hr.overtime.request'].browse(self.env.context.get('active_ids'))
        if current_id:
            current_id.rejected_reason = self.reason
            current_id.state = 'refuse'
