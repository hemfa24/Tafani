# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request


class ResCompany(models.Model):
    _inherit = "res.company"

    """
        Move This code to bi hemfa 2.0 module
    """
    # treasury_journal_id = fields.Many2one(
    #     'account.journal',
    #     string='Cash Treasury Journal ',
    #     domain=[('type', '=', 'cash')]
    # )
    # treasury_bank_journal_id = fields.Many2one(
    #     'account.journal',
    #     string='Bank Treasury  Journal',
    # )
    # treasury_cheque_journal_id = fields.Many2one(
    #     'account.journal',
    #     string='Cheque Treasury  Journal',
    # )
    # treasury_credit_account_id = fields.Many2one(
    #     'account.account',
    #     string='Credit Account',
    # )
    # treasury_debit_account_id = fields.Many2one(
    #     'account.account',
    #     string='Debit Account',
    # )


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _search(
            self, args, offset=0, limit=None, order=None,
            count=False, access_rights_uid=None
    ):
        context = self._context or {}
        allowed_company_ids = context.get('allowed_company_ids', [])
        show_type = context.get('show_type')
        if context.get('show_current_company'):
            args = [
               # ('active', '=', True),
                ('company_id', '=', int(context.get('show_current_company')))
            ]
            if show_type == 'bank':
                args += [('type', '=', 'bank')]
            else:
                args += [('type', '=', 'cash')]
        else:
            args += [
                #('active', '=', True),
                '|', ('company_id', '=', False),
                ('company_id', 'in', allowed_company_ids)
            ]

        # updated to search the code too
        return super(AccountJournal, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid
        )
