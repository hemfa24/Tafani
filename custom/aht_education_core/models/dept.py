# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class Department(models.Model):
    _name = 'aht.department'
    _rec_name = 'name'
    _description ='Department Master Defination'

    name = fields.Char("Department Name")
    dep_code = fields.Char('Dept Code')
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    percredit_charges = fields.Float(string='Per ECTS Charges')
    college = fields.Many2one('aht.college',ondelete='restrict')
    abbreviation = fields.Char('Abbreviation')
    about_dept_english= fields.Html(string='About Department')
    about_dept_kurdish= fields.Html(string='About Department')
    title_image = fields.Binary("Department Image")
    mission_english = fields.Html(string='Mission')
    vision_english = fields.Html(string='Goals')
    mission_kurdish = fields.Html(string='Mission')
    vision_kurdish = fields.Html(string='Goals')
    dept_contact = fields.Html(string='Contact')
    active=fields.Boolean(default=True)
    hod_department = fields.Many2one('hr.employee',string='Head of Department',domain=[('is_lecturer','=',True)])

    _sql_constraints = [
        ('unique_name',
         'unique(name)', 'Name should be unique as per Department!')]