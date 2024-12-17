# -*- coding: utf-8 -*-

import base64
import logging
import re

from email.utils import formataddr
from uuid import uuid4

from odoo import _, api, fields, models, modules, tools
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import ormcache, pycompat
from odoo.tools.safe_eval import safe_eval


class course_category(models.Model):
    _name = 'course.category'
    _descrption = "Course Category"

    name = fields.Char('Name')

    _sql_constraints = [
        ('unique_category',
         'unique(name)', 'Course category should be unique')]


class CourseTitle(models.Model):
    _name = 'aht.course.title'
    _description = 'Course Title'


    name=fields.Char("Title")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique!')]

class ProgramTitle(models.Model):
    _name = 'aht.courselevel'
    _description = 'Course Level'
    _rec_name ='name'

    name = fields.Char('Name')


    _sql_constraints = [
        ('unique_title_name',
         'unique(name)', 'Code should be unique per Title!')]

class Course(models.Model):
    _name = 'aht.course'

    name = fields.Many2one('aht.course.title', string="Title", required=True)
    course_category = fields.Many2one('course.category', 'Course Category', required=True)
    subject_level = fields.Many2one('aht.courselevel', "Course Level")
    # semester_system = fields.Many2one('create.semester', "Semester")
    subject_type = fields.Selection([('Theory', 'Theory'), ('Practical', 'Practical'), ('Both', 'Both')], required=1,
                                    string='Course Type', default='Theory')
    code = fields.Char("Code")
    description = fields.Text("Description")
    offering_level = fields.Selection(
        [('Institution Requirements', 'Institution Requirements'), ('College Requirements', 'College Requirements'),
         ('Departmental Requirements', 'Departmental Requirements')], string='Offering Level')
    # semester_id = fields.Many2one('ums.semester')
    subject_code = fields.Char("Course Code", default='0000')
    percredit_charges = fields.Float(string='Per ECTS Charges')
    total_course_charges = fields.Float(string='Total Course Charges', compute='_compute_total_course_charges',
                                        store=True)
    credit_hour = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'),
                                    ('3', '3'), ('4', '4')
                                       , ('5', '5'), ('6', '6'),
                                    ('7', '7'), ('8', '8'),
                                    ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')
                                    ],
                                   'ECTS/Credit', default='0')
    theory_hour = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'),
                                    ('3', '3'), ('4', '4')
                                       , ('5', '5'), ('6', '6'),
                                    ('7', '7'), ('8', '8'),
                                    ('9', '9'), ('10', '10'),
                                    ],
                                   'Theory Contact Hour', default='0', required="1")
    practical_hour = fields.Selection([('0', '0'), ('1', '1'), ('2', '2'),
                                       ('3', '3'), ('4', '4')
                                          , ('5', '5'), ('6', '6'),
                                       ('7', '7'), ('8', '8'),
                                       ('9', '9'), ('10', '10'),
                                       ],
                                      'Practical Contact Hour', required="1", default='0')
    department = fields.Many2one("aht.department", string="Department", required=0)
    college = fields.Many2one('aht.college', ondelete='restrict')
    knowledge_area = fields.Many2one('knowledge.area', "Knowledge Area")
    suggested_course_material = fields.Html()
    # domain_area = fields.Many2one('domain.name', "Domain")
    annual = fields.Boolean("Annual System")

    course_objectives = fields.Html(string='Course Objectives')
    recommended_books = fields.Html(string='Recommended Book')

    semester = fields.Boolean("Semester System")
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    active = fields.Boolean("Active", default=True)
    theory_hour_integer = fields.Integer(compute='compute_theory_hour_int', store=False)
    practical_hour_integer = fields.Integer(compute='compute_practical_hour_int', store=False)

    @api.depends('practical_hour')
    def compute_practical_hour_int(self):
        for record in self:
            if record.practical_hour:
                record.practical_hour_integer = int(record.practical_hour)

    @api.depends('theory_hour')
    def compute_theory_hour_int(self):
        for record in self:
            if record.theory_hour:
                record.theory_hour_integer = int(record.theory_hour)
    image = fields.Binary(attachment=True, string='Image')

    _sql_constraints = [
        ('unique_code',
         'unique(subject_code)', 'Course code should be unique')]

    def name_get(self):
        result = []
        name = ''
        for record in self:
            if record.name and record.subject_code:
                name = str(record.name.name) + '-' + '[' + str(record.subject_code) + ']'
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """ search full name and barcode """
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('subject_code', operator, name), ('name', operator, name)]
        return self._search(domain + args, limit=limit,access_rights_uid=name_get_uid)


    @api.onchange('clos_line')
    def onchange_clos(self):
        clos_list = []
        if len(self.clos_line) > 1:
            for rec in self.clos_line:
                if rec:
                    if rec.clo:
                        if rec.clo.name in clos_list:
                            raise UserError('Clos already exists')
                        else:
                            clos_list.append(rec.clo.name)

    @api.depends('percredit_charges', 'credit_hour')
    def _compute_total_course_charges(self):
        for record in self:
            if record.percredit_charges:
                if record.credit_hour:
                    record.total_course_charges = record.percredit_charges * float(record.credit_hour)
