# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    #Fully override to avoid Cancel related journal entries comment code button_cancel
    def set_to_return(self):
        if self.is_no_accounting_effect and self.account_cheque_type == 'incoming':
            # return
            self.no_accounting_effect_state('registered')
            return
        elif self.is_no_accounting_effect and self.account_cheque_type == 'outgoing':
            self.no_accounting_effect_state('return')
            return
            # for journal_items in self:
            #     journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
            #     journal_item_ids.button_cancel()

        account_move_obj = self.env['account.move']
        move_lines = []
        list_of_move_line = []
        # if self.re_amount:
        if self.amount:

            for journal_items in self:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])

            matching_dict = []
            for move in journal_item_ids:
                for line in move.line_ids:
                    if line.full_reconcile_id:
                        matching_dict.append(line)

            if len(matching_dict) != 0:
                rec_id = matching_dict[0].full_reconcile_id.id
                a = self.env['account.move.line'].search([('full_reconcile_id', '=', rec_id)])

                for move_line in a:
                    move_line.remove_move_reconcile()

            if self.account_cheque_type == 'incoming':
                if not self.env.user.company_id.deposite_account_id.id:
                    raise UserError(("Sorry Please First Set Deposit account in Accounting Setting."))
                vals = {
                    'date': self.cheque_receive_date,
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'state': 'draft',
                    'ref': self.cheque_number + '- ' + 'Returned',
                    'account_cheque_id': self.id
                }
                account_move = account_move_obj.create(vals)
                debit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.debit_account_id.id,
                    # 'debit' : self.re_amount,
                    'debit': self.amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, debit_vals))
                credit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.env.user.company_id.deposite_account_id.id,
                    # 'credit' : self.re_amount,
                    'credit': self.amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, credit_vals))
                account_move.write({'line_ids': move_lines})
                account_move._post(soft=False)
                # account_move.button_cancel()
                # self.status1 = 'return'
                # as docs states
                self.status1 = 'registered'
                self.cheque_return_date = datetime.now().date()
            else:
                vals = {
                    'date': self.cheque_given_date,
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'state': 'draft',
                    'ref': self.cheque_number + '- ' + 'Returned',
                    'account_cheque_id': self.id
                }
                account_move = account_move_obj.create(vals)
                debit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.credit_account_id.id,
                    'debit': self.re_amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, debit_vals))
                credit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.debit_account_id.id,
                    'credit': self.re_amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, credit_vals))
                account_move.write({'line_ids': move_lines})
                account_move._post(soft=False)
                # account_move.button_cancel()
                self.status = 'return'
                self.cheque_return_date = datetime.now().date()
            return account_move

    # Fully override to avoid Cancel related journal entries comment code button_cancel
    def set_to_bounced(self):
        if self.is_no_accounting_effect:
            self.no_accounting_effect_state('bounced')
            return
        # for journal_items in self:
        #     journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
        #     journal_item_ids.button_cancel()

        account_move_obj = self.env['account.move']
        move_lines = []
        # if self.re_amount:
        if self.amount:
            if self.account_cheque_type == 'incoming':
                self.set_to_return()
                vals = {
                    'date': self.cheque_receive_date,
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'state': 'draft',
                    'ref': self.cheque_number + '- ' + 'Bounced',
                    'account_cheque_id': self.id
                }
                account_move = account_move_obj.create(vals)
                debit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.credit_account_id.id,
                    # 'debit' : self.re_amount,
                    'debit': self.amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, debit_vals))
                credit_vals = {
                    'partner_id': self.payee_user_id.id,
                    # 'account_id' : self.payee_user_id.property_account_receivable_id.id,
                    'account_id': self.debit_account_id.id,
                    # 'credit' : self.re_amount,
                    'credit': self.amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, credit_vals))
                account_move.write({'line_ids': move_lines})
                account_move._post(soft=False)

                # account_move.button_cancel()
                self.status1 = 'bounced'
            else:
                vals = {
                    'date': self.cheque_given_date,
                    'journal_id': self.journal_id.id,
                    'company_id': self.company_id.id,
                    'state': 'draft',
                    'ref': self.cheque_number + '- ' + 'Bounced',
                    'account_cheque_id': self.id
                }
                account_move = account_move_obj.create(vals)
                debit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.credit_account_id.id,  # self.payee_user_id.property_account_payable_id.id,
                    'debit': self.re_amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, debit_vals))
                credit_vals = {
                    'partner_id': self.payee_user_id.id,
                    'account_id': self.debit_account_id.id,
                    'credit': self.re_amount,
                    'date_maturity': datetime.now().date(),
                    'move_id': account_move.id,
                    'company_id': self.company_id.id,
                }
                move_lines.append((0, 0, credit_vals))
                account_move.write({'line_ids': move_lines})
                account_move._post(soft=False)
                # account_move.button_cancel()
                self.status = 'bounced'
            return account_move

    # Fully override to avoid Cancel related journal entries comment code set_to_cancel
    def action_set_draft(self):
        for rec in self:
            # rec.set_to_cancel()
            rec.status = rec.status1 = 'draft'
            rec.re_compute_invoice()

        if rec.cheque_book_line_id:
            rec.cheque_book_line_id.is_used = False
            rec.cheque_book_line_id.account_cheque_id = False