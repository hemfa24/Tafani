from odoo import models, fields, api, _
import pytz
from dateutil import tz
from datetime import datetime


class AssignmentSubmission(models.Model):
    _name = 'aht.assignment.submission'
    _description = 'Assignment Submission'
    _rec_name = 'title'

    student = fields.Many2one('aht.student', string='Student')
    file_name = fields.Char('File Name')
    title = fields.Char('Title')
    q_file_name =  fields.Char('Question File Name')
    a_file_name =  fields.Char('Answer File Name')
    s_file_name = fields.Char('Solution File Name')
    question_file = fields.Binary(string='Question File', attachment=True)
    answer_file = fields.Binary(string="Answer File", attachment=True)
    course_offered_id = fields.Many2one('aht.course.offerings', string='Course')
    solution_file = fields.Binary(string='Solution File', attachment=True)
    available_from = fields.Datetime(store=True, string='From')
    available_to = fields.Datetime(store=True, string='To')
    is_available_to_upload = fields.Boolean(compute='check_available_upload')
    # is_allowed_to_view = fields.Boolean(compute='check_allowed_view')
    is_allowed_solution = fields.Boolean(compute='check_allowed_solution', default=False)
    state = fields.Selection([('Draft', 'Draft'), ('Submitted', 'Submitted')], default='Draft')
    # question_attachment_id = fields.Many2one("ir.attachment", string="Question File Attachment")
    # answer_attachment_id = fields.Many2one("ir.attachment", string="Answer File Attachment")
    # solution_attachment_id =fields.Many2one("ir.attachment", string="Solution File Attachment")
    
    
    @api.depends('available_from', 'available_to')
    def check_available_upload(self):
        for rec in self:
            uploaded_datetime = rec.utc_to_local(datetime.utcnow())
            rec.is_available_to_upload = True
            if rec.available_from:
                available_from = rec.utc_to_local(rec.available_from)
            if rec.available_to:
                available_to = rec.utc_to_local(rec.available_to)
            if rec.available_from and str(uploaded_datetime) < available_from:
                rec.is_available_to_upload = False
            if rec.available_to and str(uploaded_datetime) > available_to:
                rec.is_available_to_upload = False

    def submit_assignment(self):
        self.state = 'Submitted'

    def utc_to_local(self, utc_dt):
        local_tz = pytz.timezone(
            self.env.user.partner_id.tz or 'GMT')
        from_zone = tz.gettz('UTC')
        utc = datetime.strptime(str(utc_dt).split('.')[0], '%Y-%m-%d %H:%M:%S')
        # Tell the datetime object that it's in UTC time zone since
        # datetime objects are 'naive' by default
        utc = utc.replace(tzinfo=from_zone)
        # Convert time zone
        local_dt = utc.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")
        return local_dt

    @api.depends('available_from', 'available_to')
    def check_allowed_solution(self):
        for rec in self:
            if rec.available_to:
                current_datetime = fields.Datetime.now()
                available_to = rec.available_to
                if current_datetime > available_to:
                    rec.is_allowed_solution = True
                else:
                    rec.is_allowed_solution = False
            else:
                rec.is_allowed_solution = False
    
    
    def createAttachment(self, rec, file_name,file):
        
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': file,
            'res_model': 'aht.assignment.submission',
            'res_id': rec.id,
            'type': 'binary',
        })
        return attachment
    
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(AssignmentSubmission, self).create(vals_list)
    #     if res.question_file:
    #         question_file_attachment = self.createAttachment(res,res.q_file_name, res.question_file)
    #         res.write({'question_attachment_id': question_file_attachment.id})
    #     if res.answer_file:
    #         answer_file_attachment = self.createAttachment(res,res.a_file_name,res.answer_file)
    #         res.write({'answer_attachment_id': answer_file_attachment.id})
    #     if res.solution_file:
    #         solution_file_attachment = self.createAttachment(res,res.s_file_name,res.solution_file)
    #         res.write({'solution_attachment_id': solution_file_attachment.id})          
    #     return res
    #
    # def write(self, vals):
    #     res = super(AssignmentSubmission, self).write(vals)
    #     if 'question_file' in vals:
    #         att_id = self.env['ir.attachment'].search([('name', '=', self.question_file)])
    #         if att_id:
    #             vals['question_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)
    #         else:
    #             attachment = self.createAttachment(self, res.q_file_name,self.question_file)
    #             vals['question_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)
    #
    #
    #     if 'answer_file' in vals:
    #         att_id = self.env['ir.attachment'].search([('name', '=', self.answer_file)])
    #         if att_id:
    #
    #             vals['answer_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)
    #         else:
    #             attachment = self.createAttachment(self,res.a_file_name,self.answer_file)
    #             vals['answer_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)      
    #
    #
    #     if 'solution_file' in vals:
    #         att_id = self.env['ir.attachment'].search([('name', '=', self.solution_file)])
    #         if att_id:
    #
    #             vals['solution_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)
    #         else:
    #             attachment = self.createAttachment(self,res.s_file_name,self.solution_file)
    #             vals['solution_attachment_id'] = att_id.id
    #             res = super(AssignmentSubmission, self).write(vals)        
    #
    #
    #     return res
    
    
    
    
    
    
    # @api.depends('available_from', 'available_to')
    # def check_allowed_view(self):
    #     if self.available_from:
    #         available_from = self.utc_to_local(self.available_from)
    #     uploaded_datetime = self.utc_to_local(datetime.utcnow())
    #     self.is_allowed_to_view = True
    #     if self.available_from and str(uploaded_datetime) < available_from:
    #         self.is_allowed_to_view = False
