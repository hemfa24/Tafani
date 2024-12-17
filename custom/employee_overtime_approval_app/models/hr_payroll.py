# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    overtime_wages = fields.Float(compute="_calc_overtime_wages", string='Overtime Wages', store=True, default=0)

    @api.depends('employee_id', 'contract_id')
    def _calc_overtime_wages(self):
        for rec in self:
            if rec.employee_id:
                overtime_obj = self.env['hr.overtime.request'].sudo()
                overtime_ids = overtime_obj.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'done'),
                    ('overtime_date_from', '>=', rec.date_from),
                    ('overtime_date_from', '<=', rec.date_to),
                ])
                contract_id = rec.contract_id

                if not contract_id:
                    rec.overtime_wages = 0
                    continue

                overtime_sum = 0
                for overtime_id in overtime_ids:
                    if overtime_id.hourly_type == 'fx':
                        overtime_sum += overtime_id.number_of_hours * overtime_id.hourly_wage
                    else:
                        hours_per_day = contract_id.resource_calendar_id.hours_per_day
                        days_per_month = contract_id.resource_calendar_id.days_per_month
                        monthly_wage = contract_id.wage

                        hourly_rate = monthly_wage / days_per_month / hours_per_day
                        type_rate = overtime_id.overtime_type.rate
                        overtime_sum += overtime_id.number_of_hours * hourly_rate * type_rate

                rec.overtime_wages = overtime_sum
