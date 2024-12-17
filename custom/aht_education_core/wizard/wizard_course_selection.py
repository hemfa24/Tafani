from odoo import api, fields, models, _



class WizardCourseSelection(models.TransientModel):
    _name="wiz.course.selection"
    
   
    course_ids = fields.One2many('wiz.course.selection.line','wiz_course_select_id', string='Courses')
    
    
    def add_course(self):
        crs_id= self.env.context.get('active_id',False)
        if crs_id:
            
            record= self.env['course.registration.student'].browse([crs_id])
            if self.course_ids:
                line_vals=[]
                for li in self.course_ids:
                    if li.is_selected == True:
                        obj= self.env['aht.course.offerings'].search([('course_name','=',li.course_id.id)])
                        if obj:
                            line_vals.append(
                                (0, 0 ,
                                 
                                 {  'course_name':li.course_id.id,
                                     'course_offered':obj[0].id,
                                   'registration':record.id
                                     })
                                
                                )
                if record.course_ids:
                    for ol in record.course_ids:
                        record.course_ids = [(3, ol.id)]
                
                record.course_ids =line_vals           
        # obj=self.env['aht.course.offerings'].search([('class_id','=',re.current_class_id.id),('academic_year','=',re.academic_year.id)])
        # line_val=[]
        # if obj:
        #
        #     for rec in obj:
        #         line_val.append(
        #             (0, 0, {
        #             'is_selected':True,
        #             'course_id': rec.course_name.id,
        #              })
        #             )  
        #
        # self.env['wiz.course.selection'].create({'course_ids':line_val})        
        print('select button clicked!')

class WizardCourseSelectionLine(models.TransientModel):
    _name="wiz.course.selection.line"
    
    wiz_course_select_id = fields.Many2one("wiz.course.selection" , string="Wizard course sel id") 
    course_id=fields.Many2one('aht.course' ,string ="course", readonly=True)
    credit_hours = fields.Selection(related='course_id.credit_hour', store=False)
    course_code = fields.Char(related='course_id.subject_code', string='Course Code')
    is_selected = fields.Boolean(default=False)
#
# class CourseRegLinesInh(models.Model):
#     _inherit = 'course.registration.lines'
#

   
    
    
    
    