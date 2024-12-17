# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class accountPartialPayment(models.TransientModel):
    
    _name = "account.partial.payment"

    payment_id = fields.Many2one('account.payment')
    account_cheque_id = fields.Many2one('account.cheque')
    unapplied_amount = fields.Float(related="payment_id.unapplied_amount")
    unapplied_currency_amount = fields.Float('Unapplied Foreign Currency Amount',related="payment_id.unapplied_currency_amount")
    amount = fields.Float('Unapplied Amount')
    open_invoice_ids = fields.One2many('account.partial.payment.invoice','partial_payment_id')


    @api.model
    def default_get(self, fields):
        """ set default value """
        
        result = super(accountPartialPayment, self).default_get(fields)

        
        # result = {}
        rec = {}
        payment_obj = self.env['account.payment']
        invoice_obj = self.env['account.move']
        cheque_obj = self.env['account.cheque']
        
        if result.get('account_cheque_id',False):

            cheque = cheque_obj.browse(result.get('account_cheque_id',False))

            result['account_cheque_id'] = cheque.id

            invoices = invoice_obj.search([
                    ('state','=','posted'),
                    ('openning_balance_move','=',True),
                    ])

            lines = []

            if cheque.account_cheque_type == 'incoming':
                
                for invoice in invoices:
                    for line in invoice.line_ids.filtered(lambda line: line.move_id.state == 'posted' and line.partner_id.id == cheque.payee_user_id.id and not line.reconciled and line.debit > 0):
               
                        dict_line = {
                            'move_line_id':line.id,
                                                        'partner_id':line.partner_id.id,
                                                        'currency_id': invoice.currency_id.id,
                                                        'debit': line.debit,
                                                        'credit': line.credit,
                                                        'residual':line.amount_residual,
                        }
                        lines.append((0, 0, dict_line))
            
            elif cheque.account_cheque_type == 'outgoing':
                for invoice in invoices:
                    for line in invoice.line_ids.filtered(lambda line: line.move_id.state == 'posted' and line.partner_id.id == cheque.payee_user_id.id and not line.reconciled and line.credit > 0):
               
                        dict_line = {
                            'move_line_id':line.id,
                                                        'partner_id':line.partner_id.id,
                                                        'currency_id': invoice.currency_id.id,
                                                        'debit': line.debit,
                                                        'credit': line.credit,
                                                        'residual':line.amount_residual,
                        }
                        lines.append((0, 0, dict_line))
            
            dict_val = {
                        'open_invoice_ids': lines,
                        'account_cheque_id': result['account_cheque_id'],
                        'amount':cheque.amount,
                        # 'partial_payment_id':result['id'],
                        }
            rec.update(dict_val)

        if result.get('payment_id',False):
            payment = payment_obj.browse(result['payment_id'])
            result['amount'] = payment.unapplied_amount

            payment_type = payment.payment_type
            if payment_type == 'inbound':
                invoices = invoice_obj.search([
                    ('state','=','posted'),
                    ('openning_balance_move','=',True),
                    ])

                lines = []
                for invoice in invoices:
                    for line in invoice.line_ids.filtered(lambda line: line.partner_id.id == payment.partner_id.id and not line.reconciled and line.debit > 0):
               
                        dict_line = {
                            'move_line_id':line.id,
                                                        'partner_id':line.partner_id.id,
                                                        'currency_id': invoice.currency_id.id,
                                                        'debit': line.debit,
                                                        'credit': line.credit,
                                                        'residual':line.amount_residual,
                        }
                        lines.append((0, 0, dict_line))
                        
                dict_val = {
                    'open_invoice_ids': lines,
                    'payment_id': result['payment_id'],
                    'amount':payment.unapplied_amount,
                    # 'partial_payment_id':result['id'],
                    }
                rec.update(dict_val)
            elif payment_type == 'outbound':
                invoices = invoice_obj.search([
                    ('state','=','posted'),
                    ('openning_balance_move','=',True),
                    ])

                lines = []
                for invoice in invoices:
                    for line in invoice.line_ids.filtered(lambda line: line.partner_id.id == payment.partner_id.id and not line.reconciled and line.credit > 0):
               
                        dict_line = {
                            
                            'move_line_id':line.id,
                                                        'partner_id':line.partner_id.id,
                                                        'currency_id': invoice.currency_id.id,
                                                        'debit': line.debit,
                                                        'credit': line.credit,
                                                        'residual':line.amount_residual,
                        }
                        lines.append((0, 0, dict_line))
                        
                dict_val = {
                    'open_invoice_ids': lines,
                    'payment_id': result['payment_id'],
                    'amount':payment.unapplied_amount,
                    # 'partial_payment_id':result['id'],
                    }
                rec.update(dict_val)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>RECCC ",rec)
                     
        return rec

    def js_assign_outstanding_line(self, line_id,line_id_sec):
        ''' Called by the 'payment' widget to reconcile a suggested journal item to the present
        invoice.

        :param line_id: The id of the line to reconcile with the current invoice.
        '''
        self.ensure_one()
        lines = self.env['account.move.line'].browse(line_id)
        lines += line_id_sec # self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        return lines.reconcile()
         

    def action_partial_payment(self):
        for rec in self:
            if rec.payment_id:
                payment = rec.payment_id
                
                # for payment in purchase.payment_ids:
                dest_line = payment.move_id.line_ids.filtered(lambda mv: mv.account_id.id == payment.destination_account_id.id)
            
                
                for line in rec.open_invoice_ids:
                    rec.js_assign_outstanding_line(dest_line.id,line.move_line_id)

                # rec._compute_amount()
            if rec.account_cheque_id:
                cheque = rec.account_cheque_id
                journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',cheque.id)])
                
                if cheque.account_cheque_type == 'outgoing':
                    dest_line = journal_item_ids.line_ids.filtered(lambda mv: mv.move_id.state == 'posted' and mv.account_id.id == cheque.debit_account_id.id)
                else:
                    dest_line = journal_item_ids.line_ids.filtered(lambda mv: mv.move_id.state == 'posted' and mv.account_id.id == cheque.credit_account_id.id)

                
                for line in rec.open_invoice_ids:
                    rec.js_assign_outstanding_line(dest_line.id,line.move_line_id)

                # rec._compute_amount()
            return

class accountPartialPaymentInvoice(models.TransientModel):
    """
    Inheritance to make payments in batches
    """
    _name = "account.partial.payment.invoice"

    move_line_id = fields.Many2one('account.move.line')
    partner_id = fields.Many2one('res.partner')
    currency_id = fields.Many2one('res.currency')
    debit = fields.Monetary()
    credit = fields.Monetary()
    residual = fields.Float('Residual to Reconcile')
    partial_payment_id = fields.Many2one('account.partial.payment')