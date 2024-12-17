from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree



class ProgramTitle(models.Model):
    _name="program.title"
    
    
    name= fields.Char(string = "Program Title")
    
class ProgramLevel(models.Model):
    _name="program.level"
    
    name= fields.Char(string = "Program Level")
    
class DegreeAbbr(models.Model):
    _name="degree.abbreviation"
    
    name= fields.Char(string = "Degree Abbreviation")    
    
class ProgramDuration(models.Model):
    _name="program.duration"
    
    name= fields.Char(string = "Program Duration")
    
class ProgramDependency(models.Model):
    _name="program.depends"
    
    name= fields.Char(string = "Program Depends on")
    
class AhtProgram(models.Model):
    _name="aht.program"
    _rec_name ="complete_name"
    
    complete_name =fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    department_id= fields.Many2one("aht.department" , string="Department")
    program_level_id = fields.Many2one("program.level" , string="Program Level")
    degree_abbr_id =  fields.Many2one("degree.abbreviation" , string="Degree Abbreviation" , required=True)
    program_title_id = fields.Many2one("program.title" , string="Program Title" , required=True)
    program_code = fields.Char(string="Program Code" , required=True)
    program_depends_id= fields.Many2one("program.depends",string="Based On")
    program_duration_id= fields.Many2one("program.duration",string="Program Duration")
     
    @api.depends('degree_abbr_id', 'program_title_id','program_code')
    def _compute_complete_name(self):
        for nm in self:
            
            nm.complete_name = '%s - %s - %s' % (nm.degree_abbr_id.name, nm.program_title_id.name, nm.program_code)
            

     
               