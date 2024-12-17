# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def js_assign_outstanding_line(self, line_id):
        res = super(AccountMove, self).js_assign_outstanding_line(line_id)
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'payment':
            if line_id:
                lines = self.env['account.move.line'].browse(line_id)
                if lines and lines[0].move_id.account_cheque_id:
                    account_cheque = lines[0].move_id.account_cheque_id
                    if account_cheque:
                        account_cheque.get_treasury_payment_commission(outstanging_inv_ids=self)
        return res
