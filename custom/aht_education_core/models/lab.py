from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError



class LabGroup(models.Model):
    _name = 'lab.group'
    _description = 'Lab group'
    
    name=fields.Char(string = "Name" )
    
    
class StuLabAlloc(models.Model):
    _name ="lab.allocate.student"  
    
    _rec_name = 'course_offered'
    
    academic_year= fields.Many2one('aht.academic.year', string="Academic Year",required=True) 
    labgroup_id = fields.Many2one("lab.group",string ="Lab group" ,required=True )
    college_id  = fields.Many2one("aht.college" ,string="College")
    department_id= fields.Many2one("aht.department" ,string="Department")
    class_id =fields.Many2one("course.registration.class" ,string="Class")
    lab_responsible_ids =fields.Many2many("hr.employee" ,string="Lab Responsible" ,domain="[('is_lecturer' ,'=',True)]")
    student_ids =fields.Many2many("aht.student",string="Student",required=True)
    course_offered=fields.Many2one('aht.course.offerings',string="Course", required=True)
    
    
    @api.onchange('course_offered','labgroup_id')
    def _onchangeCourseLab(self):
        if self.course_offered:
            reg_lin =self.env['course.registration.lines'].search([('course_offered','=',self.course_offered.id)])
            if reg_lin:
                stud_rec = reg_lin.mapped('student_id')
                if self.labgroup_id:
                    stud_rec =stud_rec.filtered(lambda r,g=self.labgroup_id:r.labgroup_id !=g)
                return {'domain': {'student_ids': [('id', 'in', stud_rec.ids)]} }
    
    
    @api.model_create_multi
    def create(self, vals_list):
        res= super(StuLabAlloc ,self).create(vals_list)
        if res.student_ids:
            if res.labgroup_id:
                for st in res.student_ids:
                    st.labgroup_id  = res.labgroup_id.id
        
        return res
    
    # @api.onchange('student_ids')
    # def CourseLabcheck(self):
    #     if self:
    #         if not self.course_offered and not self.labgroup_id:
    #             raise ValidationError(_("first select course and lab group"))
    # @api.depends('name', 'parent_id.complete_name')
    # def _compute_complete_name(self):
    #     for plan in self:
    #         if plan.parent_id:
    #             plan.complete_name = '%s / %s' % (plan.parent_id.complete_name, plan.name)
    #         else:
    #             plan.complete_name = plan.name
    
    
    
    
    
    
    
    
    
    
    