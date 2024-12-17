# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrLoanLine(models.Model):
    _inherit = "hr.loan"

    check = fields.Boolean("Check")
    remain_amount = fields.Float("Remain Amount")
    payment_ids = fields.Many2many("account.payment")
    cheque_ids = fields.Many2many("account.cheque")

    @api.constrains('loan_amount')
    def _default_remain_amount(self):
        for loan in self:
            loan.remain_amount = loan.loan_amount

    def _compute_remain_amount(self):
        for rec in self:
            total_paid = 0

            for payment in rec.payment_ids.filtered(
                    lambda p: p.state not in ['draft', 'cancel'] and p.payment_model_id == rec.id and p.payment_model_name == 'loan' ):
                total_paid += payment.amount
            for cheque in rec.cheque_ids.filtered(
                    lambda c: c.status not in ['draft', 'cancel'] and c.payment_model_id == rec.id and c.payment_model_name == 'loan'):
                total_paid += cheque.amount

            if total_paid <= rec.loan_amount:
                rec.remain_amount = rec.loan_amount - total_paid
            else:
                rec.remain_amount = 0


class SalaryAdvance(models.Model):
    _inherit = "salary.advance"

    check = fields.Boolean("Check")
    remain_amount = fields.Float("Remain Amount")
    payment_ids = fields.Many2many("account.payment")
    cheque_ids = fields.Many2many("account.cheque")

    @api.constrains('advance')
    def _default_remain_amount(self):
        for loan in self:
            loan.remain_amount = loan.advance

    def _compute_remain_amount(self):
        for rec in self:
            total_paid = 0

            for payment in rec.payment_ids.filtered(
                    lambda p: p.state not in ['draft', 'cancel'] and p.payment_model_id == rec.id and p.payment_model_name == 'advance'):
                total_paid += payment.amount
            for cheque in rec.cheque_ids.filtered(
                    lambda c: c.status not in ['draft', 'cancel'] and c.payment_model_id == rec.id and c.payment_model_name == 'advance'):
                total_paid += cheque.amount

            if total_paid <= rec.advance:
                rec.remain_amount = rec.advance - total_paid
            else:
                rec.remain_amount = 0


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    amount = fields.Float("Amount", compute='_compute_amount', store=True)
    check = fields.Boolean("Check")
    remain_amount = fields.Float("Remain Amount")
    payment_ids = fields.Many2many("account.payment")
    cheque_ids = fields.Many2many("account.cheque")

    @api.constrains('amount')
    def _default_remain_amount(self):
        for rec in self:
            rec.remain_amount = rec.amount

    def _compute_remain_amount(self):
        for rec in self:
            total_paid = 0

            for payment in rec.payment_ids.filtered(
                    lambda p: p.state not in ['draft', 'cancel'] and p.payment_model_id == rec.id and p.payment_model_name == 'payslip'):
                total_paid += payment.amount
            for cheque in rec.cheque_ids.filtered(
                    lambda c: c.status not in ['draft', 'cancel'] and c.payment_model_id == rec.id and c.payment_model_name == 'payslip'):
                total_paid += cheque.amount

            if total_paid <= rec.amount:
                rec.remain_amount = rec.amount - total_paid
            else:
                rec.remain_amount = 0

    @api.depends('employee_id', 'line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.line_ids.filtered(lambda l: l.code == 'NET').total


class accountPayment(models.Model):
    _inherit = "account.payment"

    move_ids = fields.Many2many('account.move')
    loan_ids = fields.Many2many('hr.loan')
    salary_advance_ids = fields.Many2many('salary.advance')
    payslip_ids = fields.Many2many('hr.payslip')
    payment_model_name = fields.Selection(
        [('none', 'None'), ('loan', 'Loan'), ('advance', 'Advance'), ('payslip', 'Payslip')],
        default='none')
    payment_model_id = fields.Integer()

    @api.onchange('partner_type', 'partner_id')
    def onchange_partner_employee_set_ops(self):
        for rec in self:
            if rec.partner_type == 'employee' and rec.partner_id:
                payslip_ids = self.env['hr.payslip'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'done'),
                    ('remain_amount', '>', 0),
                    ('refund_payslip_id', '=', False),
                    ('credit_note', '=', False),
                ])
                rec.payslip_ids = payslip_ids

                loan_ids = self.env['hr.loan'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'approve'),
                    ('remain_amount', '>', 0),
                ])
                rec.loan_ids = loan_ids

                salary_advance_ids = self.env['salary.advance'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'approve'),
                    ('remain_amount', '>', 0),
                ])
                rec.salary_advance_ids = salary_advance_ids

    def action_post(self):
        res = super().action_post()

        for rec in self:
            is_checked = False
            for line in rec.loan_ids.filtered(lambda l: l.check):
                rec.payment_model_name = 'loan'
                rec.payment_model_id = line.id
                line._compute_remain_amount()
                line.total_paid_amount = line.loan_amount - line.remain_amount
                line.check = False
                is_checked = True
                break

            if is_checked:
                break

            for line in rec.salary_advance_ids.filtered(lambda l: l.check):
                rec.payment_model_name = 'advance'
                rec.payment_model_id = line.id
                line._compute_remain_amount()
                line.check = False
                is_checked = True
                break

            if is_checked:
                break

            for line in rec.payslip_ids.filtered(lambda l: l.check):
                rec.payment_model_name = 'payslip'
                rec.payment_model_id = line.id
                line._compute_remain_amount()
                line.check = False
                break
        return res

    def action_draft(self):
        res = super().action_draft()

        for rec in self:
            if rec.payment_model_name == 'loan':
                loan_obj = self.env['hr.loan'].sudo().browse(rec.payment_model_id)
                if loan_obj:
                    loan_obj._compute_remain_amount()
                    loan_obj.total_paid_amount = loan_obj.loan_amount - loan_obj.remain_amount
                rec.payment_model_name = 'none'
                rec.payment_model_id = None

            elif rec.payment_model_name == 'advance':
                advance_obj = self.env['salary.advance'].sudo().browse(rec.payment_model_id)
                if advance_obj:
                    advance_obj._compute_remain_amount()
                rec.payment_model_name = 'none'
                rec.payment_model_id = None

            elif rec.payment_model_name == 'payslip':
                payslip_obj = self.env['hr.payslip'].sudo().browse(rec.payment_model_id)
                if payslip_obj:
                    payslip_obj._compute_remain_amount()
                rec.payment_model_name = 'none'
                rec.payment_model_id = None

        return res

    def write(self, vals):
        for record in self:
            for field, new_value in vals.items():
                if hasattr(record, field):
                    old_value = record[field]
                    if old_value == 'employee' and new_value == 'supplier' and not vals.get('partner_id', False):
                        vals['partner_type'] = 'employee'
        result = super().write(vals)
        return result
