# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partialPayment(models.Model):
    _inherit = 'account.cheque'

    openning_balance_payment = fields.Boolean('Opening Balance Payment')

    unapplied_amount = fields.Float(compute="get_unapplied")
    unapplied_currency_amount = fields.Float('Unapplied Foreign Currency Amount',compute="get_unapplied")

    def open_reconcile_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')

        journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',self.id)])

        if self.account_cheque_type == 'outgoing':
                
            mv_line =   journal_item_ids.line_ids.filtered(lambda r:r.account_id.id == self.debit_account_id.id)
        else:
            
            mv_line =   journal_item_ids.line_ids.filtered(lambda r:r.account_id.id == self.credit_account_id.id)
            

        ids = mv_line._reconciled_lines()
        action['domain'] = [('id', 'in', ids)]
        return action


    def get_unapplied(self):
        for rec in self:
            rec.unapplied_amount = 0
            rec.unapplied_currency_amount = 0
            journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',rec.id)])
                
            if rec.account_cheque_type == 'outgoing':
                
                mv_line =   journal_item_ids.line_ids.filtered(lambda r:r.account_id.id == rec.debit_account_id.id)
            else:
                
                mv_line =   journal_item_ids.line_ids.filtered(lambda r:r.account_id.id == rec.credit_account_id.id)

                    
            # mv_line = rec.move_id.line_ids.filtered(lambda r:r.account_id.id == rec.destination_account_id.id)
            if len(mv_line) == 1:
                rec.unapplied_amount = abs(mv_line.amount_residual)
                rec.unapplied_currency_amount = abs(mv_line.amount_residual_currency)

class partialPayment(models.Model):
    _inherit = 'account.payment'

    unapplied_amount = fields.Float(compute="get_unapplied")
    unapplied_currency_amount = fields.Float('Unapplied Foreign Currency Amount',compute="get_unapplied")
    openning_balance_payment = fields.Boolean('Opening Balance Payment')


    def get_unapplied(self):
        for rec in self:
            rec.unapplied_amount = 0
            rec.unapplied_currency_amount = 0
            mv_line = rec.move_id.line_ids.filtered(lambda r:r.account_id.id == rec.destination_account_id.id)
            if len(mv_line) == 1:
                rec.unapplied_amount = abs(mv_line.amount_residual)
                rec.unapplied_currency_amount = abs(mv_line.amount_residual_currency)

    def open_reconcile_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
        mv_line = self.move_id.line_ids.filtered(lambda r:r.account_id.id == self.destination_account_id.id)

        ids = mv_line._reconciled_lines()
        action['domain'] = [('id', 'in', ids)]
        return action
