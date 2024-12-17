# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class FiscalYearClosing(models.TransientModel):
    _name = "generating.closing.fiscalyear"
    _description = "Generating Closing Entry"


    fy_id = fields.Many2one(
        'account.fiscalyear',
        'Fiscal Year to Close',
        required=True,
        help="Select a fiscal year to close"
    )

    journal_id = fields.Many2one(
        "account.journal",
        "Opening Entries Journal",
        required=True,
        domain="[('code','=','COEJ')]",
    )

    def data_save(self):
        """
        This generating close account fiscalyear
        """
        journalObj = self.env['account.journal']
        moveObj = self.env['account.move']

        paymentObj = self.env['account.payment']

        account_move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        currency_obj = self.env['res.currency']

        account_type = ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']

        journal_ids = journalObj.search([
            ('type', 'in', ['bank', 'cash', 'purchase', 'sale'])
        ])

        start_date = self.fy_id.date_start
        date_stop = self.fy_id.date_stop

        checking_draft = moveObj.search([
            ('state', '=', 'draft'),
            ('date', '>=', start_date),
            ('date', '<=', date_stop),
            ('journal_id', 'in', journal_ids.ids)
        ])

        checking_payment = account_move_line_obj.search([
            ('account_id.reconcile', '=', True),
            ('date', '>=', start_date),
            ('date', '<=', date_stop)
        ])

        checking_payment = checking_payment.filtered(
            lambda x: x.amount_residual != 0
        )

        account_ids = account_obj.sudo().search([('account_type', 'in', account_type)])
        move_lines = account_move_line_obj.sudo().search([
            ('account_id', 'in', account_ids.ids),
            ('date', '>=', start_date),
            ('date', '<=', date_stop)
        ])
        print("...", sum(move_lines.mapped("debit")))
        print(" CRDIt", sum(move_lines.mapped("credit")))
        Total_Balance = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
        print("Total_Balance", Total_Balance)

        if checking_draft or checking_payment:
            raise UserError(_(
                        """
                        Theres Draft Or Unreconciled Entries..
                        That Needs To be Checked!!!
                        """))
        """
            @cash 1 : If the Credit Side Is Greater Then Its Profit
            @cash 2 : If The Debit Side Is Greater Then Its Loss
        """

        annual_equity_type_id = account_obj.search([
            ('coa_account_type', '=', 'annual_equity_type')
        ])

        pl_equity_type_id = account_obj.search([
            ('coa_account_type', '=', 'pl_equity_type')
        ])

        earning_id = account_obj.search([
            ('coa_account_type', '=', 'earning')
        ])
        print("ANULL ", annual_equity_type_id, pl_equity_type_id, earning_id)
        if not annual_equity_type_id or\
                not pl_equity_type_id or not earning_id:
            raise UserError(_(
                        """
                        Not configure

                        The Account Type Equity & Current year Earning.
                        """))
        
        # create the close move
        vals = {
            "name": "/",
            "ref": "Close Period : " + str(start_date) + '-' + str(date_stop),
            "date": date_stop,
            "journal_id": self.journal_id.id,
        }

        if Total_Balance > 0:
            """"
                Case 1: If The P&L Result Is Profit
                ( Credit side greater ) negative Value

                - Debit: 9999 - Undistributed Profits/Losses Account
                - Credit: 303 - Annual Profit and Loss
            """

            debit_account_id = earning_id
            credit_account_id = annual_equity_type_id
            lines = []

            #Debit Value
            lines.append((0, 0, {
                    'name': _('Close Balance : Debit Centralisation'),
                    'centralisation': 'debit',
                    'partner_id': False,
                    'account_id': debit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'date': date_stop,
                    'debit': Total_Balance,
                    'credit': 0.0,
                }))

            #Credit Value
            lines.append((0, 0, {
                    'name': _('Close Balance : Credit Centralisation'),
                    'centralisation': 'credit',
                    'partner_id': False,
                    'account_id': credit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'date': date_stop,
                    'debit': 0.0,
                    'credit': Total_Balance,
                }))

            print('\n\n -- - -------  ', lines)
            vals.update({'line_ids': lines})
            move_id = moveObj.create(vals)
            move_id.action_post()
        else:
            """"
                Case 1: If The The P&L Result Is Loss
                ( Debit side greater ) Positive value

                - Debit: 303 - Annual Profit and Loss
                - Credit: 9999 - Undistributed Profits/Losses Account
            """

            debit_account_id = annual_equity_type_id
            credit_account_id = earning_id
            lines = []

            #Debit Value
            lines.append((0, 0, {
                    'name': _('Close Balance : Debit Centralisation'),
                    'centralisation': 'debit',
                    'partner_id': False,
                    'account_id': debit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'date': date_stop,
                    'debit': Total_Balance,
                    'credit': 0.0,
                }))

            #Credit Value
            lines.append((0, 0, {
                    'name': _('Close Balance : Credit Centralisation'),
                    'centralisation': 'credit',
                    'partner_id': False,
                    'account_id': credit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'date': date_stop,
                    'debit': 0.0,
                    'credit': Total_Balance,
                }))
            vals.update({'line_ids': lines})
            move_id = moveObj.create(vals)
            move_id.action_post()
        
