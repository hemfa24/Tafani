# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class BiReportAccountTax(models.AbstractModel):
    _inherit = 'report.bi_account_tax_report.bi_report_account_tax'

    def _sql_from_amls_one(self):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE %s GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self):
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        # compute the tax amount
        domain = []
        if options.get('branch_ids'):
            domain = [('branch_id', 'in', options.get('branch_ids'))]
        sql = self._sql_from_amls_one()
        if options.get('branch_ids'):
            tables, where_clause, where_params = self.env['account.move.line']._where_calc([
                ('parent_state', '=', 'posted'),
                ('company_id', '=', self.env.company.id),('branch_id', 'in', options.get('branch_ids'))
            ]).get_sql()
        else:
            tables, where_clause, where_params = self.env['account.move.line']._where_calc([
                ('parent_state', '=', 'posted'),
                ('company_id', '=', self.env.company.id)
            ]).get_sql()

        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['tax'] = abs(result[1])

        # compute the net amount
        sql2 = self._sql_from_amls_two()
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
            'custom_branch':data['form']['custom_branch']
        }
