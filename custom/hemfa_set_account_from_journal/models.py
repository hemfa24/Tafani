# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _




class AccountAccountType(models.Model):
    _inherit = "account.move"

    @api.onchange('journal_id')
    def _onchange_journal_idE(self):
        for rec in self:
            if rec.state=='draft' and rec.move_type=='out_invoice':
                new_account = rec.journal_id.default_account_id.id
                list_accounts =[]
                obj = self.env['account.journal'].search([
                    ('type','=','sale')
                ])
                for acc_id in obj.default_account_id:
                    list_accounts.append(acc_id.id)
                if new_account:
                    for line in rec.line_ids:
                        if line.account_id.id in list_accounts:
                            print(line.account_id)
                            line.sudo().write({
                                'account_id':new_account
                            })
