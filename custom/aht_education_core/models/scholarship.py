from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree

class Scholarship(models.Model):
    _name="aht.scholarship"
    
    name=fields.Char(string= "Name",required=True)
    
class ScholarshipAllocation(models.Model):
    _name="scholarship.allocation"
    _rec_name ="complete_name" 
    
   

    
    complete_name =fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    academic_year= fields.Many2one('aht.academic.year', string="Academic Year", required=True ,states={'Confirm': [('readonly', True)]} ) 
    student_id = fields.Many2one("aht.student" ,string="Student",  required=True ,states={'Confirm': [('readonly', True)]})    
    user_id =fields.Many2one("res.users" ,string="Allocate by"  ,states={'Confirm': [('readonly', True)]})
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Confirm', 'Confirm')], string='State', default='Draft' )
    
    scholarship_type = fields.Selection([
        ('Percentage', 'Percentage'),
        ('Fixed', 'Fixed')], string='Scholarship type'  ,states={'Confirm': [('readonly', True)]})
    
    value = fields.Float(string="Value"  ,states={'Confirm': [('readonly', True)]})
    scholarship_id= fields.Many2one("aht.scholarship" , string="Scholarship", required=True)
    
    
    _sql_constraints = [
        ('code_student_uniq', 'unique (student_id)', 'Student should be unique as per academic year!')
    ]
   
    def btn_confirm(self):
        self.write({'state':'Confirm'}) 
        
    
    
    
    @api.depends('student_id', 'scholarship_id')
    def _compute_complete_name(self):
        for nm in self:
            
            nm.complete_name = '%s - %s' % (nm.scholarship_id.name, nm.student_id.first_name)
            
    
    
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(ScholarshipAllocation,self).get_view(view_id, view_type, **options) 
        if not self.env.user.has_group('aht_education_core.group_scholarship_manager'):
            temp = etree.fromstring(result['arch'])
            temp.set('create', '0')
            temp.set('edit', '0')
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
       
        return result          
    