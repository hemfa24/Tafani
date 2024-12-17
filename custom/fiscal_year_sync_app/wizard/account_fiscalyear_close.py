# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class AccountFiscalyearClose(models.TransientModel):
    _name = "account.fiscalyear.close"
    _description = "Fiscalyear Close"

    fy_id = fields.Many2one(
        "account.fiscalyear",
        "Fiscal Year to close",
        required=True,
        help="Select a Fiscal year to close",
    )
    fy2_id = fields.Many2one("account.fiscalyear", "New Fiscal Year", required=True)
    journal_id = fields.Many2one(
        "account.journal",
        "Opening Entries Journal",
        required=True,
        domain="[('type','=','situation'),('code','=','OPEJ')]",
    )
    period_id = fields.Many2one(
        "account.period", "Opening Entries Period", required=True
    )
    report_name = fields.Char(
        "Name of new entries",
        required=True,
        help="Give name of the new entries",
        default="End of Fiscal Year Entry",
    )

    def data_save(self):
        obj_acc_move = self.env["account.move"]
        obj_acc_move_line = self.env["account.move.line"]
        obj_acc_account = self.env["account.account"]
        obj_acc_journal_period = self.env["account.journal.period"]
        for data in self:
            fy_id = data.fy_id
            fy2_id = data.fy2_id
            self._cr.execute(
                "SELECT id FROM account_period WHERE date_stop < (SELECT date_start FROM account_fiscalyear WHERE id = %s)",
                (str(fy2_id.id),),
            )
            fy_period_set = ",".join(map(lambda id: str(id[0]), self._cr.fetchall()))
            self._cr.execute(
                "SELECT id FROM account_period WHERE date_start > (SELECT date_stop FROM account_fiscalyear WHERE id = %s)",
                (str(fy_id.id),),
            )
            fy2_period_set = ",".join(map(lambda id: str(id[0]), self._cr.fetchall()))

            if not fy_period_set or not fy2_period_set:
                raise UserError(
                    _("The periods to generate opening entries cannot be found.")
                )

            period = data.period_id
            new_fyear = fy2_id
            old_fyear = fy_id
            print("F Year  - -- -- ", new_fyear, old_fyear)
            new_journal = data.journal_id
            company_id = new_journal.company_id.id
            print("company_id", company_id)

            if not new_journal.profit_account_id or not new_journal.loss_account_id:
                raise UserError(
                    _("The journal must have default credit and debit account.")
                )
            if (not new_journal.centralisation) or new_journal.entry_posted:
                raise UserError(
                    _(
                        "The journal must have centralized counterpart without the Skipping draft state option checked."
                    )
                )

            annual_equity_type_id = obj_acc_account.search([
                ('coa_account_type', '=', 'annual_equity_type')
            ])

            pl_equity_type_id = obj_acc_account.search([
                ('coa_account_type', '=', 'pl_equity_type')
            ])

            earning_id = obj_acc_account.search([
                ('coa_account_type', '=', 'earning')
            ])

            if not annual_equity_type_id or\
                not pl_equity_type_id or not earning_id:
                raise UserError(_(
                            """
                            Not configure

                            The Account Type Equity & Current year Earning.
                            """))
            # delete existing move and move lines if any
            move_ids = obj_acc_move.search(
                [("journal_id", "=", new_journal.id), ("period_id", "=", period.id)]
            )
            if move_ids:
                move_line_ids = obj_acc_move_line.search(
                    [("move_id", "in", move_ids.ids)]
                )
                move_line_ids.remove_move_reconcile()
                move_line_ids.unlink()
                move_ids.unlink()

            self._cr.execute(
                "SELECT id FROM account_fiscalyear WHERE date_stop < %s",
                (str(new_fyear.date_start),),
            )
            result = self._cr.dictfetchall()
            fy_ids = [x["id"] for x in result]
            fiscalyear_ids = self.env["account.fiscalyear"].browse(fy_ids)
            query_get_clause = obj_acc_move_line.with_context(
                {"fiscalyear": fiscalyear_ids}
            )._query_get()
            query_get_clause_val = query_get_clause[2]
            print(query_get_clause_val[0])
            new_list = []
            for i in query_get_clause_val[0]:
                if type(i) == int:
                    new_list.append(i)
            print(tuple(new_list))
            x = tuple(new_list)
            result_list = "(%s)" % ", ".join(map(repr, x))

            query_line = f"account_move_line.parent_state in {query_get_clause_val[1]}"
            query_line += f" AND account_move_line.period_id in (SELECT id FROM account_period WHERE fiscalyear_id IN {result_list})"
            

            obj_acc_move_line = self.env["account.move.line"]
            obj_acc_account = self.env["account.account"]
            y_start_date = self.period_id.date_start - relativedelta(years=1)
            y_end_date = self.period_id.date_stop - relativedelta(years=1)


            
            close_entery = obj_acc_move.search([
                ('date', '=', y_end_date),
                ('journal_id.code', '=', 'COEJ')
            ])
            if not close_entery:
                raise UserError(_(
                        """
                        Please Generate The Closing Entry First..!!!
                        """))

            # create the opening move
            vals = {
                "name": "/",
                "ref": "Opening Entries " + str(period.date_start),
                "period_id": period.id,
                "date": period.date_start,
                "journal_id": new_journal.id,
                "amount_total": 1000,
            }
            move_id = obj_acc_move.create(vals)

            # 1. report of the accounts with defferal method == 'unreconciled'
            Partners = self.env['res.partner'].search([
                ('parent_id', '=', False),
                ('customer_rank', '>', 0),
                '|',
                ('supplier_rank', '>', 0),
                '|',
                ('company_id', '=', self.env.company.id),
                ('company_id', '=', False)]
            )

            account_ids = obj_acc_account.sudo().search([
                ('close_method', '=', 'unreconciled')
            ])

            for acc in account_ids:
                for partner in Partners:
                    print("partnerpartnerpartner", partner, y_start_date, y_end_date)
                    move_lines = obj_acc_move_line.search([
                        ('partner_id', '=', partner.id),
                        ('account_id', '=', acc.id),
                        ('date', '>=', y_start_date),
                        ('date', '<=', y_end_date)
                    ])
                    Total_Balance = sum(move_lines.mapped("credit")) - sum(move_lines.mapped("debit"))
                    
                    if Total_Balance > 0:
                        line_id = obj_acc_move_line.create({
                            'name': 'Balance',
                            'partner_id': partner.id,
                            'account_id': acc.id,
                            'move_id': move_id.id,
                            'journal_id': move_id.journal_id.id,
                            'period_id': move_id.period_id.id,
                            'date': move_id.period_id.date_stop,
                            'debit': Total_Balance,
                            'credit': 0.0,
                        })
                        self.env.cr.execute('update account_move_line set partner_id=%s, name=%s where id=%s', (partner.id, 'Balance', line_id.id))
                    else:
                        if Total_Balance < 0:
                            line_id = obj_acc_move_line.create({
                                'name': 'Balance',
                                'partner_id': partner.id,
                                'account_id': acc.id,
                                'move_id': move_id.id,
                                'journal_id': move_id.journal_id.id,
                                'period_id': move_id.period_id.id,
                                'date': move_id.period_id.date_stop,
                                'debit': 0.0,
                                'credit': Total_Balance,
                            })
                            self.env.cr.execute('update account_move_line set partner_id=%s, name=%s where id=%s', (partner.id, 'Balance', line_id.id))

            # 3. report of the accounts with defferal method == 'balance'
            print("..........Balance Details -- - --")
            self._cr.execute(
                """
                SELECT a.id
                FROM account_account a
                WHERE a.account_type not in ('view', 'consolidation')
                  AND a.company_id = %s
                  AND a.close_method = %s ORDER BY id asc""",
                (
                    company_id,
                    "balance",
                ),
            )
            result = self._cr.dictfetchall()
            account_ids = [x["id"] for x in result]
            query_1st_part = """
                    INSERT INTO account_move_line (
                         debit, credit, balance, name, date, date_maturity, move_id, journal_id, period_id, fiscalyear_id, 
                         account_id, currency_id, company_currency_id, amount_currency, company_id, parent_state, display_type) VALUES
            """
            query_2nd_part = ""
            query_2nd_part_args = []
            amount_currency_total = 0.0
            for account in obj_acc_account.with_context(
                {"fiscalyear": old_fyear}
            ).browse(account_ids):
                company_currency_id = self.env.user.company_id.currency_id
                account_debit_line_ids = self.env["account.move.line"].search(
                    [
                        ("account_id", "=", account.id),
                        ("debit", "!=", 0.0),
                        ("fiscalyear_id", "=", old_fyear.id),
                    ]
                )
                
                account_debit = sum([line.debit for line in account_debit_line_ids])

                account_credit_line_ids = self.env["account.move.line"].search(
                    [
                        ("account_id", "=", account.id),
                        ("credit", "!=", 0.0),
                        ("fiscalyear_id", "=", old_fyear.id),
                    ]
                )
                account_credit = sum([line.credit for line in account_credit_line_ids])
                amount_balance = account_debit - account_credit

                if amount_balance < 0.0:
                    amount_currency = -amount_balance
                else:
                    amount_currency = amount_balance
                if not company_currency_id.is_zero(abs(amount_balance)):
                    if query_2nd_part:
                        query_2nd_part += ","
                    query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    if amount_balance < 0.0:
                        amount_currency_total += abs(amount_balance)
                        query_2nd_part_args += (
                            amount_balance if amount_balance > 0.0 else 0.0,
                            -amount_balance if amount_balance < 0.0 else 0.0,
                            amount_balance or 0.0,
                            data.report_name,
                            period.date_start,
                            period.date_stop,
                            move_id.id,
                            new_journal.id,
                            period.id,
                            new_fyear.id,
                            account.id,
                            company_currency_id.id or None,
                            company_currency_id.id or None,
                            -amount_currency,
                            account.company_id.id,
                            "draft",
                            "product",
                        )
                    else:
                        print("ELSEEEE", account)
                        print("ELSE amount_currency_total ", amount_balance, amount_currency_total)
                        query_2nd_part_args += (
                            amount_balance,
                            -amount_balance if amount_balance < 0.0 else 0.0,
                            amount_balance or 0.0,
                            data.report_name,
                            period.date_start,
                            period.date_stop,
                            move_id.id,
                            new_journal.id,
                            period.id,
                            new_fyear.id,
                            account.id,
                            company_currency_id.id or None,
                            company_currency_id.id or None,
                            amount_currency_total,
                            account.company_id.id,
                            "draft",
                            "product",
                        )
            
            if query_2nd_part:
                print ("query_2nd_part_args", query_2nd_part_args)
                print("query_1st_part", query_1st_part)
                print("query_2nd_part", query_2nd_part)
                #STOP
                self._cr.execute(
                    query_1st_part + query_2nd_part, tuple(query_2nd_part_args)
                )
                self.env.invalidate_all()
            # validate and centralize the opening move
            print("move_id = = = = = = = == ", move_id.line_ids)
            for line in move_id.line_ids:
                print("lineline", line.move_id)
                line.move_id = move_id.id
            move_id.validate()

            # create the journal.period object and link it to the old fiscalyear
            acc_journal_period_id = obj_acc_journal_period.search(
                [("journal_id", "=", new_journal.id), ("period_id", "=", period.id)]
            )
            if not acc_journal_period_id:
                acc_journal_period_id = obj_acc_journal_period.create(
                    {
                        "name": (new_journal.name or "") + ":" + (period.code or ""),
                        "journal_id": new_journal.id,
                        "period_id": period.id,
                    }
                )
            self._cr.execute(
                "UPDATE account_fiscalyear "
                "SET end_journal_period_id = %s "
                "WHERE id = %s",
                (acc_journal_period_id.id, old_fyear.id),
            )
            self.env.invalidate_all()
            return {"type": "ir.actions.act_window_close"}
