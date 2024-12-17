# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class resPartnerOpBalanceWizard(models.TransientModel):
    _name = 'res.partner.op_balance.wizard'

    partner_id = fields.Many2one('res.partner')
    openning_balance = fields.Float(related="partner_id.receivable_openning_balance",readonly="1")
    openning_balance_bill = fields.Float(related="partner_id.payable_openning_balance",readonly="1")
    
    # invoice_balance = fields.Float(related="partner_id.total_invoiced")

    currency_id = fields.Many2one('res.currency', related="partner_id.currency_id" ,readonly="1" )

    invoice_balance = fields.Monetary( related = "partner_id.total_invoiced",readonly="1" )
    bill_balance = fields.Monetary( related = "partner_id.total_bill",readonly="1" )

    is_bill = fields.Boolean()
    
    def show_invoices(self):
        # self.partner_id.action_view_partner_invoices()

        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if not self.is_bill:
            action['domain'] = [
                ('move_type', 'in', ('out_invoice', 'out_refund')),
                ('partner_id', 'child_of', self.partner_id.id),
            ]
            action['context'] = {'default_move_type':'out_invoice', 'move_type':'out_invoice', 'journal_type': 'sale', 'search_default_unpaid': 1}
        else:
            action['domain'] = [
            ('move_type', 'in', ('in_invoice', 'in_refund')),
            ('partner_id', 'child_of', self.partner_id.id),
        ]
        action['context'] = {'default_move_type':'in_invoice', 'move_type':'in_invoice', 'journal_type': 'purchase', 'search_default_unpaid': 1}
        
        return action
        