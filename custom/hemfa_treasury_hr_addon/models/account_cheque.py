# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    loan_ids = fields.Many2many('hr.loan')
    salary_advance_ids = fields.Many2many('salary.advance')
    payslip_ids = fields.Many2many('hr.payslip')
    payment_model_name = fields.Selection(
        [('none', 'None'), ('loan', 'Loan'), ('advance', 'Advance'), ('payslip', 'Payslip')],
        default='none')
    payment_model_id = fields.Integer()

    @api.onchange('payee_type', 'employee_id')
    def onchange_set_employee_partner(self):
        for rec in self:
            if rec.payee_type == 'employee':
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

                if not rec.employee_id:
                    rec.payee_user_id = False
                if rec.employee_id:
                    rec.payee_user_id = rec.employee_id.user_id.partner_id.id if rec.employee_id.user_id else rec.employee_id.address_home_id.id

    def set_to_submit(self):
        res = super().set_to_submit()

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

    def action_set_draft(self):
        res = super().action_set_draft()

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

    def set_to_cancel(self):
        res = super().set_to_cancel()

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
