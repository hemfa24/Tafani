# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = "res.company"

    treasury_journal_id = fields.Many2one(
        'account.journal',
        string='Cash Treasury Journal ',
        domain=[('type', '=', 'cash')]
    )
    treasury_bank_journal_id = fields.Many2one(
        'account.journal',
        string='Bank Treasury  Journal',
    )
    treasury_cheque_journal_id = fields.Many2one(
        'account.journal',
        string='Cheque Treasury  Journal',
    )
    # treasury_credit_account_id = fields.Many2one(
    #     'account.account',
    #     string='Credit Account',
    # )
    # treasury_debit_account_id = fields.Many2one(
    #     'account.account',
    #     string='Debit Account',
    # )
