# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from datetime import datetime, date, timedelta
import pytz


class CourseOffering(models.Model):
    _name = 'aht.course.offerings'

    _rec_name = 'course_name'
    _order = 'academic_year,id desc'

    crn = fields.Char('CRN')
    main_language = fields.Many2one('res.lang', string='Main Languages')
    allow_labattendant_attendance = fields.Boolean(string='Attendant Can Mark Attendance', default=True)
    course_name = fields.Many2one("aht.course", string="Course", required=True)
    course_type = fields.Selection(related='course_name.subject_type', store=False)
    credit_hours = fields.Selection(related='course_name.credit_hour', store=False)
    lab_attendant = fields.Many2many('hr.employee', 'lab_attendance_course_offered_rel', 'offered_id', 'lecturer_id',
                                     string='Lab Attendants')
    academic_year = fields.Many2one('aht.academic.year')
    course_code = fields.Char(related='course_name.subject_code', string='Course Code')
    course_charges = fields.Float(string='Course Charges', related='course_name.total_course_charges', store=False)
    course_duration = fields.Integer(string='Duration(Weeks)')
    offering_level = fields.Selection(related='course_name.offering_level', string='Offering Level', store=False)
    faculty = fields.Many2one("hr.employee", "Course instructor", required=True, domain=[('is_lecturer', '=', True)])
    lecturer_username = fields.Char(related='faculty.user_id.name', string='instructor Name')
    is_alternative_faculity = fields.Boolean('Alternative Lecturers')
    alternative_faculity = fields.Many2many('hr.employee', 'alternativelecturer_course_offered_rel', 'offered_id',
                                            'lecturer_id', string="Alternative Lecturer")
    class_id = fields.Many2one('course.registration.class', string='Class', required=False)

    # semester_id = fields.Many2one('ums.semester')
    course_outline = fields.Html(string='Course Outline')
    recommended_books = fields.Html(string='Recommended Book')
    capacity = fields.Integer("Enrollment Capacity", required=True, track_visibility='onchange')
    enrolled = fields.Integer(string="Student Enrolled")
    remaining_seats = fields.Integer("Remaining Seats", compute='_compute_remainings_seats', store=False)
    course_category = fields.Many2one(related='course_name.course_category', store=False, string='Course Category')
    active = fields.Boolean('Active', default=True)
    rejection_reason_store = fields.Char(string='Rejection Reason')
    course_level = fields.Many2one(related='course_name.subject_level', store=False, string='Course Level')
    state = fields.Selection([('Draft', 'Draft'),
                              ('Waiting For Approval', 'Waiting For Approval')
                                 ,
                              ('Approved', 'Approved'), ('reject', 'Rejected')], default='Draft',
                             track_visibility='onchange')
    department = fields.Many2one('aht.department')
    college = fields.Many2one(related='department.college', store=False)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    prefinal_marks = fields.Float(string='Prefinal Marks', track_visibility='onchange')
    final_marks = fields.Float(string='Final Marks', track_visibility='onchange')
    theory_hours = fields.Integer(related='course_name.theory_hour_integer', store=False)
    practical_hours = fields.Integer(related='course_name.practical_hour_integer', store=False)
    
    
    
    
    
    student_ids=fields.Many2many("aht.student",string="students")
    # def name_get(self):
    #     result = []
    #     name = ''
    #     for record in self:
    #         if record.course_name and record.crn:
    #             name = str(record.course_name.name.name) + '-' + '[' + str(record.crn) + ']'
    #         result.append((record.id, name))
    #     return result

    @api.depends('capacity', 'enrolled')
    def _compute_remainings_seats(self):
        for record in self:
            record.remaining_seats = record.capacity - record.enrolled

    def btn_submit(self):
        self.write({'state': 'Waiting For Approval'})

    def btn_approve(self):
        self.write({'state': 'Approved'})

    def btn_reset(self):
        self.write({'state': 'Draft'})

    def btn_reject(self):
        self.write({'state': 'reject'})
