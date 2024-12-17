from odoo import api, fields, models, _
from lxml import etree
from odoo.exceptions import ValidationError, UserError


class CourseRegLines(models.Model):
    _name = 'course.registration.lines'
    _description = 'Course Reg lines'

    registration = fields.Many2one('course.registration.student',string='Course Name', required=False)
    course_offered=fields.Many2one('aht.course.offerings')
    
    course_name = fields.Many2one("aht.course", string="Course" ,related="course_offered.course_name")
    course_code = fields.Char(related='course_name.subject_code', string='Course Code')
    credit_hours = fields.Selection(related='course_name.credit_hour', store=False)
    student_id = fields.Many2one('aht.student', string='Student', related="registration.student_id" )
    
    course_charges = fields.Float(string="Course charges" ,compute="clacCourseCharges" , store=True) 
    x_css = fields.Html(string='', sanitize=False, compute='_compute_css', store=False)
   
    @api.depends('course_name.credit_hour','course_name.percredit_charges')
    def clacCourseCharges(self):
        for res in self:
            if res.course_offered:
                course_rec = self.env['aht.course'].search([('id','=',res.course_offered.course_name.id)])
                if course_rec:
                    res.course_charges = int(course_rec.credit_hour) * course_rec.percredit_charges
                else:    
                    res.course_charges = 0    
            else:    
                res.course_charges = 0
           
   
    def _compute_css(self):
        for application in self:
            if not self.env.user.has_group('aht_education_core.group_registration_manager') :
                application.x_css = '<style>.o_list_record_remove {display: none !important;}</style>'
            else:
                application.x_css = False
    # o_list_record_remove text-center
class CourseRegistration(models.Model):
    _name = 'course.registration.student'
    _rec_name ="complete_name" 
    
    complete_name =fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    student_id = fields.Many2one('aht.student', string='Student', required=True ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]},)
    academic_year= fields.Many2one('aht.academic.year', required=True ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]},)
    registration_date = fields.Date('Registration Date', default=fields.Date.today(), required=True ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]},)
    current_class_id = fields.Many2one('course.registration.class', string='Current Class', required=True, default=lambda self: self._get_current_class_id() ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]},)
    next_class_id = fields.Many2one('course.registration.class', string='Next Class', required=True ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]})
    course_ids = fields.One2many('course.registration.lines','registration', string='Courses')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], string='State', default='draft')

    department_id= fields.Many2one("aht.department" , string="Department" ,required=True ,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]})
    college_id = fields.Many2one("aht.college",string="College",required=True,states={'draft': [('readonly', False)] ,'submitted': [('readonly', True)], 'approved': [('readonly', True)] ,'rejected': [('readonly', True)]})
    fee_total = fields.Float(string="Fee Amount", compute="clacFee" ,readonly=True)
    discount = fields.Float(string="Discount")
    discount_amount = fields.Float(string="Total Fee" ,readonly= True)
    
    scholarship_alloc_id = fields.Many2one("scholarship.allocation" ,string="Scholarship",readonly= True)
    sd_amount = fields.Float(string="scholarship amount")
    @api.depends('student_id', 'academic_year','registration_date')
    def _compute_complete_name(self):
        for nm in self:
            
            nm.complete_name = '%s - %s - %s' % (nm.academic_year.name, nm.student_id.first_name, nm.registration_date)

    
    @api.onchange("student_id")
    def _onchangeStudent(self):
        self.scholarship_alloc_id=''
        if self.student_id:
            scholarship_rec = self.env['scholarship.allocation'].search([('student_id' , '=',self.student_id.id)])
            if scholarship_rec:
                self.scholarship_alloc_id =  scholarship_rec.id
                
                
                
                
    @api.depends('course_ids.course_charges' ,'discount','scholarship_alloc_id','scholarship_alloc_id.scholarship_type','scholarship_alloc_id.value')
    def clacFee(self):   
        for res in self:
            course_total=0.0
            res.discount_amount =0.0
# =======
#             res.discount=0.0
# >>>>>>> 16.0
            if res.course_ids:
                course_total = sum(res.course_ids.mapped('course_charges'))
                res.fee_total =course_total
                # res.sd_amount = res.fee_total
                res.discount_amount = res.fee_total - res.discount
            else:    
                res.fee_total = course_total   
                res.discount_amount =course_total
                
            if res.scholarship_alloc_id:
                res.discount=0.0
                if res.scholarship_alloc_id.scholarship_type =='Fixed':
                    res.discount =res.scholarship_alloc_id.value 
                    res.sd_amount=res.fee_total -res.scholarship_alloc_id.value 
                    # res.discount = res.sd_amount
                    # if res.discount:
                    #         res.sd_amount =res.sd_amount -res.discount
                    #         res.discount_amount = res.sd_amount
                    # else: 
                    res.discount_amount = res.sd_amount       
                    #       res.discount_amount =res.scholarship_amount
                    
                elif  res.scholarship_alloc_id.scholarship_type =='Percentage':
                        percentage_val = (res.fee_total* res.scholarship_alloc_id.value)/100
                        res.discount= percentage_val
                        res.sd_amount = res.fee_total-percentage_val
                        # res.discount = res.sd_amount
                        # if res.discount:
                        #     res.sd_amount -= res.discount
                        #     res.discount_amount = res.sd_amount
                        # else: 
                        res.discount_amount = res.sd_amount       
                
                
            if self.discount:
                self.discount_amount = self.fee_total -self.discount 
            # if res.scholarship_alloc_id:
            #     if res.scholarship_alloc_id.scholarship_type =='Fixed':
            #
            #         res.sd_amount=res.fee_total -res.scholarship_alloc_id.value 
            #         res.discount = res.sd_amount
            #         # if res.discount:
            #         #         res.sd_amount =res.sd_amount -res.discount
            #         #         res.discount_amount = res.sd_amount
            #         # else: 
            #         res.discount_amount = res.sd_amount       
            #         #       res.discount_amount =res.scholarship_amount
            #
            #     elif  res.scholarship_alloc_id.scholarship_type =='Percentage':
            #             percentage_val = (res.fee_total* res.scholarship_alloc_id.value)/100
            #             res.sd_amount = res.fee_total-percentage_val
            #             res.discount = res.sd_amount
            #             # if res.discount:
            #             #     res.sd_amount -= res.discount
            #             #     res.discount_amount = res.sd_amount
            #             # else: 
            #             res.discount_amount = res.sd_amount       
            #             # res.discount_amount =res.fee_total-percentage_val
    #
    # @api.onchange('discount' ,'fee_total')
    # def _onchangeFeeDiscounnt(self):
    #     if self.discount:
    #         self.discount_amount = self.fee_total -self.discount
    #

    

            
            
    # @api.depends('course_ids.course_charges') 
    # def updateDiscountedfee(self): 
    #     for res in self:
    #         res.discount_amount = res.fee_total - res.discount
    #

    @api.model
    def _get_current_class_id(self):
        student = self.env['aht.student'].browse(self._context.get('active_id'))
        return student.class_id.id if student else False

    def submit_registration(self):
        self.write({'state': 'submitted'})

    def approve_registration(self):
        self.write({'state': 'approved'})
        self.student_id.write({'class_id': self.next_class_id.id,
                               'academic_year':self.academic_year.id,
                               'college_id':self.college_id.id, 
                               'department_id':self.department_id.id,
                               'state':'enrolled'})
# =======
#         self.student_id.write({'class_id': self.next_class_id.id})
# >>>>>>> 16.0
        if self.course_ids:
            for li in self.course_ids:
                if li.course_offered.remaining_seats <= 0:
                    raise UserError(_(f'No seat available for course {li.course_offered.course_name.display_name}'))
                li.course_offered.enrolled += 1
                li.course_offered.student_ids=  li.course_offered.student_ids + self.student_id
    def reject_registration(self):
        self.write({'state': 'rejected'})

    def select_course(self):
        obj=self.env['aht.course.offerings'].search([('class_id','=',self.current_class_id.id),('state','=','Approved'),('academic_year','=',self.academic_year.id)])
        line_val=[]
        if obj:
           
            for rec in obj:
                line_val.append(
                    (0, 0, {
                    'is_selected':True,
                    'course_id': rec.course_name.id,
                     })
                    )  
        return {
            'name': _('Select Courses'),
            'res_model': 'wiz.course.selection',
            'view_mode': 'form',
            'view_id': self.env.ref('aht_education_core.view_select_course_form').id,
            'context': {
                'default_course_ids': line_val,
                'default_course_registration_student_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        
        
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(CourseRegistration,self).get_view(view_id, view_type, **options) 
        # if self.env.user.has_group('aht_education_core.group_registration_student'):
        #     temp = etree.fromstring(result['arch'])
        #     temp.set('create', '0')
        #     temp.set('edit', '0')
        #     temp.set('delete', '0')
        #     result['arch'] = etree.tostring(temp)
       
        return result      
