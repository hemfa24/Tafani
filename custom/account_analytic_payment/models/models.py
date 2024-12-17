
from odoo import api, fields, models, tools, _
# import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import UserError
import json
from odoo.tools import float_is_zero, float_compare




class AccountMove(models.Model):
    _inherit = 'account.move'

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    @api.onchange('analytic_distribution')
    def onchange_method(self):
        if self.analytic_distribution and self.move_type == 'out_refund':
            for line in self.line_ids:
                line.analytic_distribution = self.analytic_distribution
            for line in self.invoice_line_ids:
                line.analytic_distribution = self.analytic_distribution


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def create(self, vals):
        result = super(AccountMoveLine, self).create(vals)
        if result.move_id.analytic_distribution and result.move_id.move_type == 'out_refund':
            result.write({'analytic_distribution': result.move_id.analytic_distribution})
        return result
class AccountChequePayment(models.Model):
    _inherit = 'account.cheque'

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    salesperson_id = fields.Many2one(
        string='Sales person',
        comodel_name='res.users',
        ondelete='restrict',
        related='payee_user_id.user_id',
        readonly=True,
        store=True

    )

    def action_outgoing_cashed(self):

        for rec in self:

            if rec.is_no_accounting_effect:
                rec.no_accounting_effect_state('cashed')
                continue
            # account_cheque = self.env['account.cheque'].browse(rec.id)
            account_move_obj = self.env['account.move']
            move_lines = []
            # if account_cheque.re_amount:

            vals = {
                'date': rec.cheque_given_date,
                'journal_id': rec.journal_id.id,
                'company_id': rec.company_id.id,
                'state': 'draft',
                'ref': rec.cheque_number + '- ' + 'Cashed',
                'account_cheque_id': rec.id,
                'invoice_user_id': self.salesperson_id.id
            }
            account_move = account_move_obj.create(vals)
            debit_vals = {
                'partner_id': rec.payee_user_id.id,
                'account_id': rec.credit_account_id.id,
                # 'debit' : account_cheque.re_amount,
                'debit': rec.amount,
                'date_maturity': datetime.now().date(),
                'move_id': account_move.id,
                'company_id': rec.company_id.id,
                'analytic_distribution': self.analytic_distribution
            }
            move_lines.append((0, 0, debit_vals))
            credit_vals = {
                'partner_id': rec.payee_user_id.id,
                'account_id': rec.journal_id.default_account_id.id,
                # 'credit' : account_cheque.re_amount,
                'credit': rec.amount,
                'date_maturity': datetime.now().date(),
                'move_id': account_move.id,
                'company_id': rec.company_id.id,
                'analytic_distribution': self.analytic_distribution
            }
            move_lines.append((0, 0, credit_vals))
            account_move.write({'line_ids': move_lines})

            account_move._post(soft=False)

            cheque_move = self.env['account.move'].search(
                [('is_move_to_reconcile', '=', True), ('state', '=', 'posted'), ('account_cheque_id', '=', rec.id)])
            dest_line = cheque_move.line_ids.filtered(lambda mv: mv.account_id.id == rec.debit_account_id.id)

            ids = []
            for line in rec.invoice_ids.filtered(lambda inv: inv.check == True):
                ids.append(line.id)
                line.js_assign_outstanding_line(dest_line.id)
                line._compute_amount()
            rec.paid_ids = ids

            rec.status = 'cashed'

    def set_to_submit(self):
        account_move = False
        if not self.is_no_accounting_effect:
            if self.amount:
                account_move_obj = self.env['account.move']
                move_lines = []
                if self.account_cheque_type == 'incoming':
                    vals = {
                        'commercial_partner_id': self.payee_user_id.id,
                        'date': self.cheque_receive_date,
                        'journal_id': self.journal_id.id,
                        'company_id': self.company_id.id,
                        'state': 'draft',
                        'ref': self.cheque_number + '- ' + 'Registered',
                        'account_cheque_id': self.id,
                        'is_move_to_reconcile': True,
                        'invoice_user_id': self.salesperson_id.id

                    }
                    account_move = account_move_obj.create(vals)

                    debit_vals = {
                        'partner_id': self.payee_user_id.id,
                        'account_id': self.debit_account_id.id,
                        'debit': self.amount,
                        'date_maturity': datetime.now().date(),
                        'move_id': account_move.id,
                        'company_id': self.company_id.id,
                        'analytic_distribution':self.analytic_distribution
                    }
                    move_lines.append((0, 0, debit_vals))

                    credit_vals = {
                        'partner_id': self.payee_user_id.id,
                        'account_id': self.credit_account_id.id,
                        'credit': self.amount,
                        'date_maturity': datetime.now().date(),
                        'move_id': account_move.id,
                        'company_id': self.company_id.id,
                        'analytic_distribution': self.analytic_distribution

                    }
                    move_lines.append((0, 0, credit_vals))
                    account_move.write({'line_ids': move_lines})

                    account_move._post(soft=False)
                    self.status1 = 'registered'
                else:
                    vals = {
                        'commercial_partner_id': self.payee_user_id.id,
                        'date': self.cheque_given_date,
                        'journal_id': self.journal_id.id,
                        'company_id': self.company_id.id,
                        'state': 'draft',
                        'ref': self.cheque_number + '- ' + 'Registered',
                        'account_cheque_id': self.id,
                        'is_move_to_reconcile': True,
                        'invoice_user_id' : self.salesperson_id.id
                    }
                    account_move = account_move_obj.create(vals)
                    debit_vals = {
                        'partner_id': self.payee_user_id.id,
                        'account_id': self.debit_account_id.id,
                        'debit': self.amount,
                        'date_maturity': datetime.now().date(),
                        'move_id': account_move.id,
                        'company_id': self.company_id.id,
                        'analytic_distribution': self.analytic_distribution

                    }
                    move_lines.append((0, 0, debit_vals))
                    credit_vals = {
                        'partner_id': self.payee_user_id.id,
                        'account_id': self.credit_account_id.id,
                        'credit': self.amount,
                        'date_maturity': datetime.now().date(),
                        'move_id': account_move.id,
                        'company_id': self.company_id.id,
                        'analytic_distribution': self.analytic_distribution

                    }
                    move_lines.append((0, 0, credit_vals))
                    account_move.write({'line_ids': move_lines})
                    account_move._post(soft=False)
                    self.status = 'registered'
                # return account_move
            else:
                raise UserError(_('Please Enter Amount Of Cheque'))
        else:

            self.no_accounting_effect_state('registered')

        for rec in self:

            if rec.cheque_book_line_id:
                rec.cheque_book_line_id.is_used = True
                rec.cheque_book_line_id.account_cheque_id = rec.id



class AccountPayment(models.Model):
    _inherit = 'account.payment'
    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    
    
    salesperson_id = fields.Many2one(
        string='Sales person',
        comodel_name='res.users',
        ondelete='restrict',
        related='partner_id.user_id',
        readonly=True,
        store=True
        
    )
    
    
    #move_id
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if self.move_id:
            self.move_id.invoice_user_id = self.salesperson_id
            for line in self.move_id.line_ids:
                line.analytic_distribution =self.analytic_distribution

      
        return res
    