# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class Section(models.Model):
    _name = 'course.registration.section'
    _description = 'Section'

    name = fields.Char(string='Section Name', required=True)
    class_id = fields.Many2one('course.registration.class', string='Class', required=False)
    
class ClassRegistration(models.Model):
    _name = 'course.registration.class'
    _description = 'Class Registration'
    _rec_name ="complete_name"
    
    complete_name =fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    # name = fields.Char(string='Class Name', required=True)
    section_id = fields.Many2one('course.registration.section', string='Group')
    program_id = fields.Many2one("aht.program" , string="Program")
    semester_id = fields.Many2one("course.registration.semester" , string="Semester")
    shift = fields.Selection([
        ('Morning', 'Morning'),
        (' After_Noon', 'After Noon'),
        ('Evening', 'Evening'),
        ], string='State',)
    
    @api.depends('program_id', 'semester_id','section_id' ,'shift')
    def _compute_complete_name(self):
        for nm in self:
            
            nm.complete_name = '%s%s - %s%s' % (nm.program_id.program_code, nm.semester_id.name, nm.section_id.name, nm.shift)            
    
class Semester(models.Model):
    _name ="course.registration.semester"

    name= fields.Char(string='Semester', required=True)
# =======
#
#     name = fields.Char(string='Class Name', required=True)
#     section_id = fields.Many2one('course.registration.section', string='Section')
#
# >>>>>>> 16.0

