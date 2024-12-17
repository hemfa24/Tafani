# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
import time
from datetime import datetime, timedelta
from odoo import exceptions
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class Salary_Advance_Rule(models.Model):
    _name = 'salary.advance.rule'

    name = fields.Char('Name', required=True)
    mount_limit = fields.Float('Mount Limit(%)', required=True)
    no_limit = fields.Integer('Number Limit', required=True)
    from_day = fields.Integer('Day in Month From', required=True)
    to_day = fields.Integer('Day in Month To', required=True)


class HrEmployeeContract(models.Model):
    _inherit = "hr.contract"
    salary_adv_rule = fields.Many2one('salary.advance.rule', string='Salary Advance Rule')


class SalaryAdvancePayment_Custom(models.Model):
    _inherit = "salary.advance"
    # is_paid=fields.Boolean(string="Paid")
    employee_contract_id = fields.Many2one('hr.contract', string='Contract', related='employee_id.contract_id')

    def submit_to_manager(self):
        contract_ids = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
        flag = True
        for con in contract_ids:
            rule = con.salary_adv_rule
            if self.date.day < rule.from_day or self.date.day > rule.to_day:
                flag = False

            wage_limit_value = con.wage * rule.mount_limit / 100
            advance_obj = self.env['salary.advance'].sudo().search([('employee_id', '=', self.employee_id.id),
                                                                    ('state', 'not in', ['draft', 'cancel', 'reject'])])
            advance_filtered = advance_obj.filtered(lambda x: x.date.month == self.date.month)
            advance_total = sum(advance_filtered.mapped('advance'))
            if wage_limit_value < (advance_total + self.advance):
                flag = False

            no_recs = self.env['salary.advance'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')])
            count = 0
            for rec in no_recs:
                if rec.date.month == self.date.month:
                    count += 1
            if count >= rule.no_limit:
                flag = False
        if flag == False:
            raise ValidationError(
                _('You Cannot submit to Manager for one of these reasons:\n - You Apply in not allowed days range.\n- You exceed the limit of advance allowed.\n-You exceed the limit times of requests allowed per month'))
        self.state = 'submit'

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id
        if not address.id:
            raise UserError(
                'Define home address for the employee. i.e address under private information of the employee.')
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        # for each_advance in salary_advance_search:
        #     existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
        #     if current_month == existing_month:
        #         raise UserError('Advance can be requested once in a month')
        if not self.employee_contract_id:
            raise UserError('Define a contract for the employee')
        struct_id = self.employee_contract_id.struct_id
        adv = self.advance
        amt = self.employee_contract_id.wage
        # if adv > amt and not self.exceed_condition:
        #     raise UserError('Advance amount is greater than allotted')

        if not self.advance:
            raise UserError('You must Enter the Salary Advance amount')
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise UserError("This month salary already calculated")

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.ValidationError(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        # salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
        #                                      ('state', '=', 'approve')])
        # current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        # for each_advance in salary_advance_search:
        #     existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
        #     if current_month == existing_month:
        #         raise UserError('Advance can be requested once in a month')
        if not self.debit or not self.credit or not self.journal:
            raise UserError("You must enter Debit & Credit account and journal to approve ")
        if not self.advance:
            raise UserError('You must Enter the Salary Advance amount')
        logging.info("approve request_acc of salary_advance>>>>>>>>")
        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            reference = request.name
            journal_id = request.journal.id
            move = {
                'name': 'Salary Advance Of ' + request_name + str(request.date),
                'narration': request_name,
                'partner_id': self.employee_id.user_id.partner_id.id if self.employee_id.user_id else self.employee_id.address_home_id.id,
                'ref': reference,
                'journal_id': journal_id,
                # 'move_type_custom': 'adv',
                'date': timenow,
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'partner_id': self.employee_id.user_id.partner_id.id if self.employee_id.user_id else self.employee_id.address_home_id.id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'partner_id': self.employee_id.user_id.partner_id.id if self.employee_id.user_id else self.employee_id.address_home_id.id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move.update({'line_ids': line_ids})

            draft = move_obj.create(move)
            draft.post()
            self.state = 'approve'
            return True


class SalaryRuleInput_Custom(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        amount = 0
        res = super(SalaryRuleInput_Custom, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0].id).employee_id
        adv_salary = self.env['salary.advance'].search([('employee_id', '=', emp_id.id), ('state', '=', 'approve')])
        for adv_obj in adv_salary:
            current_date = date_from.month
            date = adv_obj.date
            existing_date = date.month
            if current_date == existing_date:
                state = adv_obj.state
                if state == 'approve':
                    amount += adv_obj.advance
                for result in res:
                    if state == 'approve' and amount != 0 and result.get('code') == 'SAR':
                        result['amount'] = amount
        return res
