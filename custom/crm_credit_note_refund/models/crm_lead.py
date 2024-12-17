# -*- coding: utf-8 -*-

from odoo import fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'


    def _custom_add_creditnote(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm_credit_note_refund.action_custom_crm_credit_note")
        customer_invoice_ids = self.env['account.move'].search([('partner_id', 'child_of',self.partner_id.commercial_partner_id.id),('move_type','=','out_invoice')])
        move_ids = customer_invoice_ids.ids
        action['context'] = {
            'custom_domain_invoice_ids': move_ids
        }
        return action

    def custom_add_creditnote(self):
        return self._custom_add_creditnote()

    def action_view_credit_note_custom(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_refund_type")
        action['domain'] = [('custom_credit_note_crm_id', '=', self.id)]
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
