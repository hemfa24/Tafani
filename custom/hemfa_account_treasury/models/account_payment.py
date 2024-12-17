# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class accountPayment(models.Model):
    _inherit = "account.payment"

    move_ids = fields.Many2many('account.move')
    journal_type = fields.Selection(related="journal_id.type")
    
    @api.onchange('cheque_operation_ids', 'move_ids')
    def onchange_set_amount(self):
        for rec in self:
            amount = 0
            print ("onchange_set_amount", self)
            for line in rec.move_ids:
                if line.check:
                    # id = line.id or line.id.origin
                    # if (rec.partner_type == 'customer' or rec.partner_type == 'supplier') and rec.partner_id:
                    #     account_move = self.env['account.move']
                        # move_line = account_move.search([('id', '=', id)], limit=1)
                        # rec.write({'move_ids': [(1, move_line.id, {'check': True})]})
                        # line.curr_due_amount = move_line.amount_residual
                    amount += line.curr_due_amount
                    rec.currency_id = line.currency_id.id
            print ("A<OAIAUAUIAUAAIIAI", amount, )
            print ("STOR AVLUE ---", rec.amount)
            if rec.amount == 0.0:
                print ("Call TShsi one ")
                rec.amount = amount

    @api.onchange('partner_type', 'partner_id')
    def onchange_partner(self):
        for rec in self:
            rec.move_ids = False
            if rec.partner_type == 'customer' and rec.partner_id:
                print ("moves --- ")
                account_move = self.env['account.move']
                moves = account_move.search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('payment_state', '!=', 'paid'),
                ]
                )
                moves._compute_amount()
                print ("moves", moves)
                rec.move_ids = moves

            elif rec.partner_type == 'supplier' and rec.partner_id:
                account_move = self.env['account.move']
                moves = account_move.search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('move_type', 'in', ['in_invoice', 'in_refund']),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('payment_state', 'not in', ['paid', ]),
                    # ('amount_residual','>',0)
                ])
                moves._compute_amount()
                rec.move_ids = moves

            move_len = 0
            while move_len < len(rec.move_ids):
                rec.move_ids[move_len].curr_due_amount = moves[move_len].amount_residual
                rec.move_ids[move_len].check = False
                move_len += 1

    def action_post(self):
        res = super(accountPayment, self).action_post()
        for rec in self:
            dest_line = rec.move_id.line_ids.filtered(lambda mv: rec.destination_account_id.id in mv.account_id.ids)
            for line in rec.move_ids.filtered(lambda mv: mv.check):
                line.js_assign_outstanding_line(dest_line.id)
                line._compute_amount()
                line.curr_due_amount = line.amount_residual
        return res

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id,
                                                      self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else:  # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }
        payment_type = self.payment_type
        partner_type = self.partner_type
        if partner_type == 'employee':
            partner_type = 'supplier'

        default_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': -counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                'currency_id': currency_id,
                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if write_off_balance:
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': -write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        return line_vals_list + write_off_line_vals_list

    def act_payment_views(self, name, payment_type, partner_type ,journal_type):
        default_journal_id = self.journal_id.search([('type', '=', 'cash')], limit=1)

        action = {
            "type": "ir.actions.act_window",
            "name": _(name),
            "view_mode": "tree,form",
            "res_model": self._name,
            "context": {
                'default_journal_id': default_journal_id.id,
                'default_payment_type': payment_type,
                'default_partner_type': partner_type,
                # 'search_default_inbound_filter': 1,
                'default_move_journal_types': ('bank', 'cash'),
            },
            "domain": [('journal_id.type', '=', journal_type), ('payment_type', '=', payment_type)],
           # "domain": [('journal_id', '=', default_journal_id.id), ('payment_type', '=', payment_type)],
            "views": [[self.env.ref('account.view_account_payment_tree').id, "tree"], [self.env.ref('hemfa_account_treasury.view_account_payment_form').id, "form"]],

        }

        # if payment_type == 'outbound':
        #     action['context'].pop('search_default_inbound_filter')
        #     action['context']['search_default_outbound_filter'] = 1

        return action
