# -*- coding: utf-8 -*-
from odoo import api, models, fields
import ast


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_user_id = fields.Many2one(
        default=False,
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_distribution_ids = fields.Many2many('account.analytic.account', 'move_line_analytic_distribution_rel',
                                                 'line_id', 'analytic_distribution_id',
                                                 compute='_compute_analytic_account_id', store=True)
    enrt_sales_user_id = fields.Many2one(
        'res.users',
        string='Sales Person',
    )

    @api.depends('analytic_distribution')
    def _compute_analytic_account_id(self):
        analytic_distribution_ids = self.env['ir.config_parameter'].sudo().get_param(
            'account_dynamic_reports.analytic_distribution_ids')
        if not analytic_distribution_ids:
            self = self.sudo().search([['analytic_distribution_ids', '!=', False]])
            self.env['ir.config_parameter'].sudo().set_param('account_dynamic_reports.analytic_distribution_ids',
                                                             'Done')
        for line in self:
            if line.account_id.account_type not in ['asset_receivable', 'liability_payable']:
                if line.analytic_distribution:
                    line.analytic_distribution_ids = [
                        (6, 0, list(map(lambda x: int(x), line.analytic_distribution.keys())))]
                else:
                    line.analytic_distribution_ids = []
            for l in line.move_id.line_ids.filtered(
                    lambda x: x.account_id.account_type in ['asset_receivable', 'liability_payable']):
                l.analytic_distribution_ids = [(6, 0, list(line.move_id.line_ids.filtered(
                    lambda x: x.account_id.account_type not in ['asset_receivable',
                                                                'liability_payable']).analytic_distribution_ids.ids))]

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')

        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = ast.literal_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']),
                           ('account_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('parent_state', '=', state)]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|',
                       ('matched_debit_ids.max_date', '>', context['reconcile_date']),
                       ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

        if context.get('analytic_distribution_ids'):
            domain += [('analytic_distribution_ids', 'in', context['analytic_distribution_ids'])]

        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

        if context.get('analytic_tag_ids'):
            domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]

        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]

        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]
        elif context.get('allowed_company_ids'):
            domain += [('company_id', 'in', self.env.companies.ids)]
        else:
            domain += [('company_id', '=', self.env.company.id)]

        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            domain.append(('display_type', 'not in', ('line_section', 'line_note')))
            domain.append(('parent_state', '!=', 'cancel'))

            query = self._where_calc(domain)
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params
