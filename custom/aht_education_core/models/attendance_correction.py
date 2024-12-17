from odoo import api, fields, models, _


class StudentAttendance(models.Model):
    _name = 'attendance.correction.request'
    _description = 'Attendance correction Request'
    _order = "attendance_date, id"
    _rec_name = 'complete_name'
    
    
    
    
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    attendance_date = fields.Date(string ="Attendance Date" , required= True ,states={'Submitted': [('readonly', True)]} )
    academic_year= fields.Many2one('aht.academic.year', required=True  ,  states={'Submitted': [('readonly', True)]} )
    course_offered=fields.Many2one('aht.course.offerings', required=True  , states={'Submitted': [('readonly', True)]})
    submission_datetime= fields.Datetime(  states={'Submitted': [('readonly', True)]})
    faculty= fields.Many2one(related='course_offered.faculty' , states={'Submitted': [('readonly', True)]})
    attendance_lines= fields.One2many('student.course.attendance.lines','attendance_request_id' , states={'Submitted': [('readonly', True)]})
    class_hours = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ], string='Hours', default='1' , states={'Submitted': [('readonly', True)]})
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approve', 'Approve'),
        ('Reject', 'Reject')
        ], string='State', default='Draft')
    
    approved_by = fields.Many2one('res.users',string="Approved by" , readonly="True")
    attendance_id= fields.Many2one('student.course.attendance')
    
    
    
    
    @api.depends('attendance_date', 'course_offered')
    def _compute_complete_name(self):
        for nm in self:
            if nm.attendance_date and nm.course_offered:
                nm.complete_name = '%s - %s' % (nm.attendance_date, nm.course_offered.course_name.display_name)
            else:
                nm.complete_name  = nm.attendance_date
    
    
    
        
    def btn_approve(self):
        self.write({'state':'Approve',
                    'approved_by': self.env.user.id})
    
            
    def btn_reject(self):
        self.write({'state':'Reject',
                    'approved_by': self.env.user.id})
    
    def submit_attendance(self):
        self.write({'state': 'Submitted'})
     
    
    
    @api.onchange('course_offered')
    def _updateStudentList(self):
        try:
            if self.course_offered:
                for ol in self.attendance_lines:
                    self.attendance_lines = [(3, ol.id)]
                objs = self.env['course.registration.lines'].search([('course_offered','=',self.course_offered.id)])
                if  objs:
                    rec_list = []
                    for rec in objs:
                        rec_list.append((0, 0, {
                            'student': rec.registration.student_id.id,
                            'attendance_id':self.id}))
                    
            
                    self.attendance_lines = rec_list
        except Exception as e:
            print(e.args)