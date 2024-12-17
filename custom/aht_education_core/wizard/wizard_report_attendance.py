from odoo import api, fields, models, _

class WizardAttReport(models.TransientModel):
    _name="wizard.attendance"
    
    
    academic_year= fields.Many2one('aht.academic.year', required = True)
    type = fields.Selection([
        ('student', 'By Student'),
        ('course', 'By Course'),
        ], string='Type', default='' , required = True)
    
    
    student_id = fields.Many2one('aht.student' ,string="Student")
    course_id = fields.Many2one('aht.course.offerings', string="Course")
    report_type = fields.Selection([
        ('summary', 'Summary'),
        ('detailed', 'Detailed'),
        ], string='Type', default='summary' , required = True)
    
    
    @api.onchange('type')
    def _onchange_type(self):
        if self.type:
            if self.type == 'student':
                self.course_id = False
               
                
            if self.type == 'course':
                self.student_id = False
              
            
          
        else:
            self.student_id = False
            self.course_id = False
           
            
    def print_attendance_report(self):
       
   
        data = {
            'model': 'wizard.attendance',
            'ids': self.ids,
            'form': {
                'academic_year': self.academic_year, 'type': self.type,
            },
        }

        # ref `module_name.report_id` as refqerence.
        return self.env.ref('aht_education_core.report_attendance_qweb').report_action(self, data=data)
    
        
    