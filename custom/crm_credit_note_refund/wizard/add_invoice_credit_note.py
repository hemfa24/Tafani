# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class CRMCreditNote(models.TransientModel):
    _name = 'custom.crm.credit.note'
    _description = 'CRM Credit Notes'

    custom_invoice_id = fields.Many2one(
        'account.move',
        'Invoice',
        required=True,
    )

    def _action_reverse_custom(self):
        return self.with_context(active_ticket_model='account.move', active_move_id=self.custom_invoice_id.ids).custom_invoice_id.action_reverse()

    def action_reverse(self):
        return self._action_reverse_custom()

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
