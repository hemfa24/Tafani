from odoo import api, fields, models, _


class StudentAttendance(models.Model):
    _name = 'student.course.attendance'
    _description = 'Course Attendance for students'
    _order = "attendance_date, id"
    _rec_name = 'complete_name'
    
    
 
    
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    attendance_date = fields.Date(string ="Attendance Date" , required= True ,states={'Submitted': [('readonly', True)]} )
    academic_year= fields.Many2one('aht.academic.year', required=True  ,  states={'Submitted': [('readonly', True)]} )
    course_offered=fields.Many2one('aht.course.offerings', required=True  , states={'Submitted': [('readonly', True)]})
    submission_datetime= fields.Datetime(  states={'Submitted': [('readonly', True)]})
    faculty= fields.Many2one(related='course_offered.faculty' , states={'Submitted': [('readonly', True)]})
    attendance_lines= fields.One2many('student.course.attendance.lines','attendance_id' , states={'Submitted': [('readonly', True)]})
    class_hours = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ], string='Hours', default='1' , states={'Submitted': [('readonly', True)]})
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted')
        ], string='State', default='Draft')
    
    attendance_request_id= fields.Many2one('attendance.correction.request', string="Attendance Request" )
    class_type = fields.Selection([
        ('Theory', 'Theory'),
        ('Lab', 'Lab')],default="Theory", string='Class Type', states={'Submitted': [('readonly', True)]})
    
    lab_group_id =fields.Many2one("lab.group", string="Lab Group")
    company_id =fields.Many2one("res.company",string="Company" ,default= lambda self:self.env.company)
    attendance_type =  fields.Selection(
        selection=[
            ('Hourly', "Hourly"),
            ('Present/Absent', "Present/Absent"),
             ],
        string="Attendance type",
        compute="get_attendance_type"  
         )
    
    
    
    
    def get_attendance_type(self):
        attendance_type = self.env['ir.config_parameter'].sudo().get_param('aht_education_core.attendance_types')
        for res in self:
            res.attendance_type = attendance_type
    
    
    @api.depends('attendance_date', 'course_offered')
    def _compute_complete_name(self):
        for nm in self:
            if nm.attendance_date and nm.course_offered:
                nm.complete_name = '%s - %s' % (nm.attendance_date, nm.course_offered.course_name.display_name)
            else:
                nm.complete_name  = nm.attendance_date
    
     
    def createAttreq(self):
        for rec in self:
            vals =  {
                    'attendance_date': rec.attendance_date,
                    'academic_year' :  rec.academic_year.id,
                    'course_offered' :rec.course_offered.id,
                    'submission_datetime':rec.submission_datetime,
                    'class_hours':rec.class_hours,
                    'state':'Draft',
                    'attendance_id': rec.id
                    }
        att_requst_id =self.env['attendance.correction.request'].create(vals)
        
        if self.attendance_lines:
            al=[]
            for li in self.attendance_lines:
                al.append((0, 0, {
                    'registration' : li.registration.id,
                     'student' :li.student.id,
                     'status':li.status,
                      'attendance_request_id':att_requst_id.id
                     
                    }))
            att_requst_id.write({'attendance_lines': al})   
            
        return  att_requst_id 
    
       
    def attendance_request(self):
        att_requst_id =self.createAttreq()
        
        view_id = self.env.ref('aht_education_core.attendance_request_form_view').id 
        action = self.env["ir.actions.actions"]._for_xml_id("aht_education_core.attendance_request_action_window")
        action['res_id'] =  att_requst_id.id
        action['view_mode'] ='form'
        action['views'] = [[view_id, 'form']]
        return action
      
    
    def submit_attendance(self):
        self.write({'state': 'Submitted'})
     
    
    
    @api.onchange('course_offered','class_type','lab_group_id')
    def _updateStudentList(self):
        try:
            if self.course_offered:
                for ol in self.attendance_lines:
                    self.attendance_lines = [(3, ol.id)]
                objs = self.env['course.registration.lines'].search([('course_offered','=',self.course_offered.id),('registration.state','=','approved')])
                
                if  objs:
                 
                    
                    rec_list = []
                    for rec in objs:
                      
                        if self.class_type =='Lab':
                            for ol in self.attendance_lines:
                                self.attendance_lines = [(3, ol.id)]
                            if self.lab_group_id:    
                                lab_alloc_rec =self.env['lab.allocate.student'].search([('course_offered','=',rec.course_offered.id),('labgroup_id','=',self.lab_group_id.id)])
                                if lab_alloc_rec:
                                    for st in lab_alloc_rec.student_ids:
                                        rec_list.append((0, 0, {
                                                    'student': st.id,
                                                    'attendance_id':self.id}))
                                    
                                break    
                        else:            
                            rec_list.append((0, 0, {
                                'student': rec.registration.student_id.id,
                                'attendance_id':self.id}))
                    
            
                    self.attendance_lines = rec_list
        except Exception as e:
            print(e.args)
    
    
    
    
    
    
    
class StudentAttendanceLines(models.Model):
    _name = 'student.course.attendance.lines'
    @api.model
    def default_get(self, fields):
        res = super(StudentAttendanceLines, self).default_get(fields)
        return res

    
    company_id =fields.Many2one("res.company",string="Company" ,default= lambda self:self.env.company)
    attendance_type =  fields.Selection(
        selection=[
            ('Hourly', "Hourly"),
            ('Present/Absent', "Present/Absent"),
             ],
        string="Attendance type",
        compute="get_attendance_type"  
         )
    
    attendance_id= fields.Many2one('student.course.attendance')
    attendance_request_id= fields.Many2one('attendance.correction.request', string="Attendance Request" )
    registration = fields.Many2one('course.registration.student',string='student reg', required=False)
    student = fields.Many2one('aht.student', string='Student', required=True)
    status = fields.Selection([
        ('Absent', 'Absent'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4')], 
        string='Status', 
        default='1')
    att_status = fields.Selection([
        ('Absent', 'Absent'),
        ('Present', 'Present')],default="Present",
        string='Status', 
        )

    def get_attendance_type(self):
        attendance_type = self.env['ir.config_parameter'].sudo().get_param('aht_education_core.attendance_types')
        for res in self:
            res.attendance_type = attendance_type
    