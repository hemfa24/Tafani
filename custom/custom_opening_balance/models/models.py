# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta
from itertools import groupby

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from odoo.osv.expression import AND, OR
from odoo.service.common import exp_version


class PosConfig(models.Model):
    _inherit = "pos.config"

    opening_cash = fields.Float(string="Openning Cash ", default=0.0)
    default_cash = fields.Boolean(string="Default Cash Amount")

    # def set_opening_cash(self, val):
    #     self.ensure_one()
    #     self.sudo().write({"cash_register_balance_start": val})
    

class POsSissen(models.Model):
    _inherit = 'pos.session'
    
    def action_pos_session_open(self):
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state == 'opening_control'):
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            if session.config_id.cash_control and not session.rescue:
                last_session = self.search([('config_id', '=', session.config_id.id), ('id', '!=', session.id)], limit=1)
                #session.cash_register_balance_start = last_session.cash_register_balance_end_real  # defaults to 0 if lastsession is empty
            else:
                values['state'] = 'opened'
            session.write(values)
        return True
    
    
    def set_cashbox_pos(self, cashbox_value, notes):
        self.state = 'opened'
        self.opening_notes = notes
        self.cash_register_balance_start = cashbox_value
        if not self.config_id.default_cash:
            difference = cashbox_value - self.cash_register_balance_start
            self.sudo()._post_statement_difference(difference, True)
            self._post_cash_details_message('Opening', difference, notes)
            
    @api.depends('payment_method_ids', 'order_ids', 'cash_register_balance_start')
    def _compute_cash_balance(self):
        for session in self:
            cash_payment_method = session.payment_method_ids.filtered('is_cash_count')[:1]
            if cash_payment_method:
                total_cash_payment = 0.0
                last_session = session.search([('config_id', '=', session.config_id.id), ('id', '<', session.id)], limit=1)
                result = self.env['pos.payment']._read_group([('session_id', '=', session.id), ('payment_method_id', '=', cash_payment_method.id)], ['amount'], ['session_id'])
                if result:
                    total_cash_payment = result[0]['amount']

                if session.state == 'closed':
                    session.cash_register_total_entry_encoding = session.cash_real_transaction + total_cash_payment
                else:
                    session.cash_register_total_entry_encoding = sum(session.statement_line_ids.mapped('amount')) + total_cash_payment

                session.cash_register_balance_end = session.cash_register_balance_start + session.cash_register_total_entry_encoding
                session.cash_register_difference = session.cash_register_balance_end_real - session.cash_register_balance_end
            else:
                session.cash_register_total_entry_encoding = 0.0
                session.cash_register_balance_end = 0.0
                session.cash_register_difference = 0.0
            
    def get_closing_control_data(self):
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise AccessError(_("You don't have the access rights to get the point of sale closing control data."))
        self.ensure_one()
        orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
        payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
        pay_later_payments = orders.payment_ids - payments
        cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
        default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
        total_default_cash_payment_amount = sum(payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped('amount')) if default_cash_payment_method_id else 0
        other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
        cash_in_count = 0
        cash_out_count = 0
        cash_in_out_list = []
        last_session = self.search([('config_id', '=', self.config_id.id), ('id', '!=', self.id)], limit=1)
    
        if self.config_id.default_cash:
            lst_cloce = self.cash_register_balance_start #self.config_id.opening_cash
        else:
            lst_cloce = last_session.cash_register_balance_end_real
        for cash_move in self.sudo().statement_line_ids.sorted('create_date'):
            if cash_move.amount > 0:
                cash_in_count += 1
                name = f'Cash in {cash_in_count}'
            else:
                cash_out_count += 1
                name = f'Cash out {cash_out_count}'
            cash_in_out_list.append({
                'name': cash_move.payment_ref if cash_move.payment_ref else name,
                'amount': cash_move.amount
            })

        return {
            'orders_details': {
                'quantity': len(orders),
                'amount': sum(orders.mapped('amount_total'))
            },
            'payments_amount': sum(payments.mapped('amount')),
            'pay_later_amount': sum(pay_later_payments.mapped('amount')),
            'opening_notes': self.opening_notes,
            'default_cash_details': {
                'name': default_cash_payment_method_id.name,
                'amount':lst_cloce #last_session.cash_register_balance_end_real
                          + total_default_cash_payment_amount
                          + sum(self.sudo().statement_line_ids.mapped('amount')),
                'opening': lst_cloce, #last_session.cash_register_balance_end_real,
                'payment_amount': total_default_cash_payment_amount,
                'moves': cash_in_out_list,
                'id': default_cash_payment_method_id.id
            } if default_cash_payment_method_id else None,
            'other_payment_methods': [{
                'name': pm.name,
                'amount': sum(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('amount')),
                'number': len(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm)),
                'id': pm.id,
                'type': pm.type,
            } for pm in other_payment_method_ids],
            'is_manager': self.user_has_groups("point_of_sale.group_pos_manager"),
            'amount_authorized_diff': self.config_id.amount_authorized_diff if self.config_id.set_maximum_difference else None
        }
        
        
    # def _post_statement_difference(self, amount, is_opening):
    #     if amount:
    #         if self.config_id.cash_control:
    #             st_line_vals = {
    #                 'journal_id': self.cash_journal_id.id,
    #                 'amount': amount,
    #                 'date': self.statement_line_ids.sorted()[-1:].date or fields.Date.context_today(self),
    #                 'pos_session_id': self.id,
    #             }

    #         if amount < 0.0:
    #             if not self.cash_journal_id.loss_account_id:
    #                 raise UserError(
    #                     _('Please go on the %s journal and define a Loss Account. This account will be used to record cash difference.',
    #                       self.cash_journal_id.name))

    #             st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Loss)") + (_(' - opening') if is_opening else _(' - closing'))
    #             st_line_vals['counterpart_account_id'] = self.cash_journal_id.loss_account_id.id
    #         else:
    #             # self.cash_register_difference  > 0.0
    #             if not self.cash_journal_id.profit_account_id:
    #                 raise UserError(
    #                     _('Please go on the %s journal and define a Profit Account. This account will be used to record cash difference.',
    #                       self.cash_journal_id.name))

    #             st_line_vals['payment_ref'] = _("Cash difference observed during the counting (Profit)") + (_(' - opening') if is_opening else _(' - closing'))
    #             st_line_vals['counterpart_account_id'] = self.cash_journal_id.profit_account_id.id
    #         #if not self.config_id.default_cash:
    #         self.env['account.bank.statement.line'].create(st_line_vals)


    


