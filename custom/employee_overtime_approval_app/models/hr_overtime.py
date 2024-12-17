# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrOvertimeRequest(models.Model):
    _name = 'hr.overtime.request'
    _rec_name = 'name'
    _description = "Overtime Request"
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('validate1', 'Waiting For Department Manager'),
        ('validate2', 'Waiting For Hr Manager'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True,
                                  states={'confirm': [('readonly', False)]}, tracking=True)
    employee_department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                             readonly=True, tracking=True)
    overtime_date_from = fields.Date('Overtime From', tracking=True, default=fields.Datetime.now, required=True)
    overtime_date_to = fields.Date('Overtime To', tracking=True, default=fields.Datetime.now, required=True)
    job_id = fields.Many2one('hr.job', string='Job Position', related="employee_id.job_id", readonly=True,
                             tracking=True)
    number_of_hours = fields.Float('Number of Hours', copy=False, readonly=True,
                                   states={'draft': [('readonly', False)]}, tracking=True)
    notes = fields.Text(string='Internal Note', readonly=True, states={'draft': [('readonly', False)]})
    rejected_reason = fields.Char(string="Refused Reason", readonly=True)

    hourly_wage = fields.Float('Hourly Wage')
    parent_id = fields.Many2one('hr.overtime.request', readonly=True)
    overtime_type = fields.Many2one('hr.overtime.rate', tracking=True)
    hourly_type = fields.Selection([
        ('rt', 'Rate'),
        ('fx', 'Fixed')],
        required=True, default='rt', tracking=True
    )

    points_type = fields.Selection([
        ('employee', 'By Employee'),
        ('company', 'By Company'),
        ('department', 'By Department'),
        ('category', 'By Employee Tag')],
        string='Mode', readonly=True, required=True, default='employee', tracking=True,
        states={'draft': [('readonly', False)]},
    )
    employee_ids = fields.Many2many(
        'hr.employee', string='Employees', readonly=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
    )
    mode_company_id = fields.Many2one(
        'res.company', string='Company Mode', readonly=True,
        states={'draft': [('readonly', False)]},
    )
    department_id = fields.Many2one(
        'hr.department', string='Department',
        readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
    )
    category_id = fields.Many2one(
        'hr.employee.category', string='Employee Tag', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company
    )
    request_employee_ids = fields.Many2many(
        'hr.employee', 'hr_employee_point_request_rel',
        compute='_request_employee_ids',
        store=True,
    )

    @api.depends('points_type', 'employee_ids', 'department_id', 'category_id', 'mode_company_id')
    def _request_employee_ids(self):
        for rec in self:
            if rec.points_type == 'employee':
                rec.request_employee_ids = rec.employee_ids
            elif rec.points_type == 'department':
                rec.request_employee_ids = rec.department_id.member_ids
            elif rec.points_type == 'category':
                rec.request_employee_ids = rec.category_id.employee_ids
            elif rec.points_type == 'company':
                rec.request_employee_ids = self.env['hr.employee'].search(
                    [('company_id', '=', self.mode_company_id.id)])

    @api.constrains('employee_id')
    def _check_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_ids = [rec.employee_id.id]

    def action_confirm(self):
        self.state = 'validate1'

    def action_department_approve(self):
        self.state = 'validate2'

    def action_manager_confirm(self):
        if len(self.request_employee_ids) > 1:
            self.employee_id = None

            for rec in self.request_employee_ids:
                vals = {
                    'parent_id': self.id,
                    'employee_id': rec.id,
                    'overtime_date_from': self.overtime_date_from,
                    'overtime_date_to': self.overtime_date_to,
                    'notes': self.notes,
                    'number_of_hours': self.number_of_hours,
                    'overtime_type': self.overtime_type.id,
                    'hourly_type': self.hourly_type,
                    'hourly_wage': self.hourly_wage,
                    'points_type': self.points_type,
                    'state': 'done',
                }
                record = self.create(vals)
                record.employee_ids = [rec.id]
                record.department_id = self.department_id
                record.category_id = self.category_id
                record.mode_company_id = self.company_id

            self.state = 'done'

        elif len(self.request_employee_ids) == 1:
            self.employee_id = self.request_employee_ids.id
            self.state = 'done'
        else:
            self.state = 'done'

    def action_refuse(self):
        action = self.env.ref('employee_overtime_approval_app.action_request_rejected').read()[0]
        return action

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        res = super().create(vals)

        if self.env.user.has_group('employee_overtime_approval_app.hr_overtime_hr_manager'):
            if not res.employee_id:
                res.action_manager_confirm()

        elif self.env.user.has_group('employee_overtime_approval_app.hr_overtime_department_manager'):
            res.action_department_approve()

        else:
            if not self.env.user.employee_id:
                raise ValidationError(
                    _("You must define the employee linked to your user to submit the overtime request."))
            else:
                res['employee_id'] = self.env.user.employee_id.id

        if not res.name:
            res['name'] = self.env['ir.sequence'].next_by_code('hr.overtime.request') or 'New'

        return res


class HrOvertimeRate(models.Model):
    _name = 'hr.overtime.rate'

    name = fields.Char(required=True)
    rate = fields.Float(required=True)
