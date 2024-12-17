from odoo import models, fields, api, _


class HrLoan(models.Model):
    _inherit = 'hr.loan'

    total_paid_amount = fields.Float(string="Total Paid Amount")

    @api.depends('loan_amount', 'total_paid_amount')
    def _compute_loan_amount(self):
        for rec in self:
            rec.total_amount = rec.loan_amount
            rec.balance_amount = rec.loan_amount - rec.total_paid_amount
