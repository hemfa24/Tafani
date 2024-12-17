from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class ReportAttendance(models.AbstractModel):
    _name = 'report.aht_education_core.attendance_report_pdf'
    
    def getStatistic(self, course , wiz_obj, report_type=False):
        obj= self.env['student.course.attendance'].search([('state','=','Submitted'),('course_offered' ,'=',course.id),('academic_year','=',wiz_obj.academic_year.id)])
        
        if obj: 
            total_hrs = sum(map(int, obj.mapped('class_hours')))
            stu_lines = obj.attendance_lines.filtered(lambda r,s=wiz_obj.student_id :r.student == s)
            stu_att_lst= stu_lines.mapped('status') 
            if 'Absent' in stu_att_lst:
                stu_att_lst.pop(stu_att_lst.index('Absent'))
            prsent_hrs = sum(map(int,stu_att_lst ))
            absent_hrs =  total_hrs - prsent_hrs 
            return total_hrs,prsent_hrs,absent_hrs
        else:
            return False    
    
    
    
    def getStuStatistics(self,student_id,stu_lines,report_type=False):
        student_recs= stu_lines.filtered(lambda r,s=student_id: r.student == s)
        total_hrs = sum(map(int, stu_lines.attendance_id.mapped('class_hours')))
        if student_recs:
            stu_att_lst= student_recs.mapped('status') 
            if 'Absent' in stu_att_lst:
                stu_att_lst.pop(stu_att_lst.index('Absent'))
            prsent_hrs = sum(map(int,stu_att_lst ))
            absent_hrs =  total_hrs - prsent_hrs 
            return total_hrs,prsent_hrs,absent_hrs  
        else:
            return False
        
         
    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        course_obj = ''
        student_obj =''
        stu_lines=''
        det_stu_lines = ''
        if rec.type =='student':
            if rec.report_type == 'summary':
                
                course_by_stu = self.env['course.registration.lines'].search([('registration.academic_year','=',rec.academic_year.id),('student_id','=',rec.student_id.id)])
                course_obj=course_by_stu.mapped('course_offered') 
            
            if rec.report_type == 'detailed':
                det_stu_lines= self.env['student.course.attendance.lines'].search([('attendance_id.state','=','Submitted'), 
                                                                    ('attendance_id.academic_year','=',rec.academic_year.id),
                                                                    ('student','=',rec.student_id.id)]) 
                
        if rec.type =='course':
            if rec.report_type == 'summary' or rec.report_type == 'detailed' :
                stu_lines=self.env['student.course.attendance.lines'].search([('attendance_id.state','=','Submitted'),
                                                                              ('attendance_id.academic_year','=',rec.academic_year.id),
                                                                              ('attendance_id.course_offered','=',rec.course_id.id)])     
                
                
                student_obj = stu_lines.mapped('student')
        return {
            'docs' : docids,
            'data' : rec,
            'getStatistic':self.getStatistic,
            'student':student_obj,
            'det_stu_lines':det_stu_lines,
             'stu_lines': stu_lines,
             'getStuStatistics':self.getStuStatistics,
            'course':course_obj
            
            }