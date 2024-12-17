# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BankBookWizard(models.TransientModel):
    _inherit = 'account.bank.book.report'

    def _get_default_account_ids(self):
        journals = self.env['account.journal'].search([('type', '=', 'bank')])
        accounts = []
        for journal in journals:
            if journal.company_id.account_journal_payment_credit_account_id:
                accounts.append(journal.company_id.account_journal_payment_credit_account_id.id)
        return accounts

    account_ids = fields.Many2many(default=_get_default_account_ids)