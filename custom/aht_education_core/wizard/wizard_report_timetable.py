from odoo import api, fields, models, _

class WizardTimeTable(models.TransientModel):
    _name="wizard.timetable"
    
    academic_year= fields.Many2one('aht.academic.year', required = True)
    type = fields.Selection([
        ('lecturer', 'By Lecturer'),
        ('class', 'By Class'),
        ('room', 'By Room')], string='Type', default='' , required = True)
    
    class_id = fields.Many2one('course.registration.class', string='Class')
    lecturer_id = fields.Many2one('hr.employee', string='Lecturer')
    class_room_id = fields.Many2one( "class.room", string="Room")
    
    
    @api.onchange('type')
    def _onchange_type(self):
        if self.type:
            if self.type == 'lecturer':
                self.class_id = False
                self.class_room_id = False
                
            if self.type == 'class':
                self.lecturer_id = False
                self.class_room_id = False
            
            
            if self.type == 'room':
                self.lecturer_id = False
                self.class_id = False
        else:
            self.class_id = False
            self.class_room_id = False
            self.lecturer_id = False
            
    def print_timetable_report(self):
   
        data = {
            'model': 'wizard.timetable',
            'ids': self.ids,
            'form': {
                'academic_year': self.academic_year, 'type': self.type,
            },
        }

        # ref `module_name.report_id` as refqerence.
        return self.env.ref('aht_education_core.report_timetable_qweb').report_action(self, data=data)
    
        
        