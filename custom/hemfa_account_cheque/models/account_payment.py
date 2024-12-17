# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, formatLang


class accountPayment(models.Model):
    _inherit = "account.payment"

    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
        ('employee', 'Employees'),
    ], default='customer', tracking=True, required=True)

    # partner_type_all = fields.Selection([
    #     ('customer', 'Customer'),
    #     ('supplier', 'Vendor'),
    #     ('employee', 'Employees'),
    # ], stirng="Partner Type",default='customer', tracking=True, required=True)


    cheque_operation_ids = fields.One2many('account.cheque.operation', 'account_payment_id')
    is_cheque = fields.Boolean()
    cheque_book_id = fields.Many2one('cheque.book', 'Cheque Book', copy=False)
    cheque_book_line_id = fields.Many2one('cheque.book.line', 'Cheque Page', copy=False)
    is_no_accounting_effect = fields.Boolean('No Accounting Effect')

    
    # destination_employee_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     string='Destination Account',
    #     store=True, readonly=False,
    #     domain="[('account_type', 'in', ('asset_receivable', 'liability_payable')), ('company_id', '=', company_id)]",
    #     # check_company=True
    # )
    employee_id = fields.Many2one('hr.employee')


    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in self._get_valid_liquidity_accounts():
                liquidity_lines += line
            elif line.account_id.account_type not in ('1',) or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines



    @api.onchange('employee_id','partner_type')
    def onchange_set_employee_partner(self):
        """
        
        """
        for rec in self:
            if rec.partner_type == 'employee':
                if not rec.employee_id:
                    rec.partner_id = False
                if rec.employee_id:
                    rec.partner_id = rec.employee_id.user_id.partner_id.id if rec.employee_id.user_id else rec.employee_id.address_home_id.id
  

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        destination_account_id = False
        for rec in self:
            
            destination_account_id = rec.destination_account_id
        res = super(accountPayment,self)._compute_destination_account_id()
        for pay in self:
            if pay.partner_type == 'employee':
                if destination_account_id:
                    pay.destination_account_id = destination_account_id.id
                elif pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)
                
        return res
        

    def _get_aml_default_display_name_list(self):
        """ Hook allowing custom values when constructing the default label to set on the journal items.

        :return: A list of terms to concatenate all together. E.g.
            [
                ('label', "Vendor Reimbursement"),
                ('sep', ' '),
                ('amount', "$ 1,555.00"),
                ('sep', ' - '),
                ('date', "05/14/2020"),
            ]
        """
        self.ensure_one()
        display_map = {
            ('outbound', 'customer'): _("Customer Reimbursement"),
            ('inbound', 'customer'): _("Customer Payment"),
            ('outbound', 'supplier'): _("Vendor Payment"),
            ('inbound', 'supplier'): _("Vendor Reimbursement"),
        }
        if self.partner_type == 'employee':
            values = [
            ('label', _("Internal Transfer") if self.is_internal_transfer else display_map[('outbound', 'supplier')]),
            ('sep', ' '),
            ('amount', formatLang(self.env, self.amount, currency_obj=self.currency_id)),
        ]
        else:
            values = [
                ('label', _("Internal Transfer") if self.is_internal_transfer else display_map[(self.payment_type, self.partner_type)]),
                ('sep', ' '),
                ('amount', formatLang(self.env, self.amount, currency_obj=self.currency_id)),
            ]
        if self.partner_id:
            values += [
                ('sep', ' - '),
                ('partner', self.partner_id.display_name),
            ]
        values += [
            ('sep', ' - '),
            ('date', format_date(self.env, fields.Date.to_string(self.date))),
        ]
        return values


    # @api.onchange('destination_employee_account_id')
    # def onchange_dest_emp_set_dest(self):
    #     """
    #     in case partner type is employee then desitination must be same with emp deistnation
    #     """
    #     for rec in self:
    #         if rec.partner_type == 'employee' and rec.destination_employee_account_id:
    #             rec.destination_account_id = rec.destination_employee_account_id.id

    # @api.onchange('partner_type_all')
    # def onchange_set_partner_type_all(self):
    #     for rec in self:
    #         # rec.partner_type = False
    #         if rec.partner_type_all == 'customer':
    #             rec.partner_type == 'customer'
    #         elif rec.partner_type_all in ['supplier','employee']:
    #             rec.partner_type == 'supplier'
    
    # @api.onchange('partner_type_all','employee_id')
    # def oncahnge_partner_type_employee_id(self):
        
    #     for rec in self:
    #         rec.partner_id = False
    #         if rec.partner_type_all == 'employee' and rec.employee_id and rec.employee_id.user_id.partner_id:
    #             rec.partner_id = rec.employee_id.user_id.partner_id.id
            
    @api.onchange('journal_id')
    def onchange_journal_id_no_data_cheque_book_id(self):
        for rec in self:
            rec.cheque_book_id = rec.cheque_book_line_id = False

    @api.onchange('journal_id', 'cheque_book_id', 'payment_type')
    def onchange_journal_id_change_cheque_book_id(self):
        for rec in self:
            if not rec.journal_id or rec.payment_type != 'outbound':
                rec.cheque_book_id = rec.cheque_book_line_id = False
            if not rec.cheque_book_id:
                rec.cheque_book_line_id = False

    # @api.onchange('cheque_book_id','cheque_book_line_id')
    # def onchange_set_check_number(self):
    #     for rec in self:
    #         rec.check_number = False
    #         if rec.cheque_book_line_id:
    #             rec.check_number = rec.cheque_book_line_id.name

    # def action_draft(self):
    #     res = super(accountPayment,self).action_draft()
    #     for rec in self:
    #         if rec.cheque_book_line_id:
    #             rec.cheque_book_line_id.is_used = False
    #             rec.cheque_book_line_id.account_payment_id = False

    #     return res

    def action_post(self):


        # no need to effect accouting
        if self.is_no_accounting_effect:
            # self.move_id.button_cancel()
            # self.move_id.button_draft()
            # self.move_id.with_context(force_delete=True).unlink()
            # self.move_id.unlink()
            for line in self.move_id.with_context(check_move_validity=False, force_delete=True).line_ids:
                line.unlink()

        for rec in self:
            """
            in case cheque book
            """
            if rec.cheque_book_line_id:
                rec.cheque_book_line_id.is_used = True
                rec.cheque_book_line_id.account_payment_id = rec.id

        res = super(accountPayment, self).action_post()
        return res

    @api.onchange('partner_type', 'partner_id')
    def onchange_partner_employee_set_ops(self):
        for rec in self:
            if rec.partner_type == 'employee' and rec.partner_id:
                acp_object = self.env['account.cheque.operation']
                acps = acp_object.search([

                    ('partner_id', '=', rec.partner_id.id),
                    ('check', '=', False),
                    # '|',
                    # ('account_payment_id.state','!=','posted'),
                    # ('account_cheque_id.status','!=','done')
                ])
                acps_records = []
                # when fix dopmain use orm search only 
                for acp in acps:
                    if rec.check == False:  # acp.account_payment_id.state != 'posted' and acp.account_cheque_id.status != 'cashed':
                        acps_records.append(acp.id)
                rec.cheque_operation_ids = acps.ids
            else:
                rec.cheque_operation_ids = False

    @api.model_create_multi
    def create(self, vals_list):
        payments = super(accountPayment, self).create(vals_list)
        if len(vals_list) and vals_list[0].get('partner_type', False) == 'employee':
            payments.partner_type = 'employee'

        return payments

    @api.onchange('partner_type')
    def onchange_partner_type_set_partner_domain(self):
        for rec in self:
            if rec.partner_type == 'employee':
                emps = self.env['hr.employee'].search(['|', ('user_id', '!=', False), ('address_home_id', '!=', False)])
                emp_partners = []
                for emp in emps:
                    emp_partners.append(
                        emp.user_id.partner_id.id if emp.user_id else emp.address_home_id.id
                    )
                domain = {'partner_id': [('id', 'in', emp_partners)]}
                return {'domain': domain}
            else:
                domain = {'partner_id': ['|', ('parent_id', '=', False), ('is_company', '=', True)]}
                return {'domain': domain}



    # def act_cash_payments(self, name, payment_type, partner_type):
    #     default_journal_id = self.journal_id.search([('type', '=', 'cash')], limit=1)
    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": _(name),
    #         "view_mode": "tree,form",
    #         "res_model": self._name,
    #         "context": {
    #             'default_journal_id': default_journal_id.id,
    #             'default_payment_type': payment_type,
    #             'default_partner_type': partner_type,
    #             'search_default_inbound_filter': 1,
    #             'default_move_journal_types': ('bank', 'cash'),
    #         },
    #         "domain": [('is_cheque', '=', False), ('journal_id', '=', default_journal_id.id), ('payment_type', '=', payment_type)],
    #         "views": [[self.env.ref('account.view_account_payment_tree').id, "tree"], [self.env.ref('bi_account_cheque_custom.view_account_payment_journal_cash_form').id, "form"]],
    #
    #     }
