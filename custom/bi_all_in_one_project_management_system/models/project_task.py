# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta,date
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from odoo.http import request
import time



class Projecttask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", 'mail.thread']

    def task_timesheet_reminder(self):

        context = self._context
        current_uid = context.get('uid')
        current_user =self.env['res.users'].browse(current_uid)    
        task_obj = self.env['project.task'].search([('user_ids','=',current_user.id)])   
        for task in task_obj:
            if task.total_hours_spent > task.planned_hours:
                template_id = self.env['ir.model.data']._xmlid_lookup(
                                                      'bi_all_in_one_project_management_system.email_template_task_timesheet_reminder')[2]
        
                email_template_obj = self.env['mail.template'].browse(template_id)
                if template_id:
                    values = email_template_obj.generate_email(task.id, fields=['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                    values['email_from'] = current_user.email
                    values['res_id'] = False
                    values['author_id'] = current_user.partner_id.id
                    mail_mail_obj = self.env['mail.mail']
                    mail_create_id = mail_mail_obj.sudo().create(values)
                    if mail_create_id:
                        mail_create_id.sudo().send()
        return True

    @api.model
    def _cron_task_reminder(self):
        sus_id = self.env['res.partner'].browse(SUPERUSER_ID)
        for task in self.env['project.task'].search([]):
            for tasks_id in self.env['res.config.settings'].search([],order="id desc", limit=1):
                if task.date_deadline !=False:
                    if task.reminder !=False:
                        reminder_date = datetime.strptime(str(task.date_deadline),'%Y-%m-%d').date()
                        today = datetime.now().date()
                        if tasks_id.first_date == today:
                            if tasks_id.first_date.month == today.month:
                                if tasks_id.first_date.day == today.day:
                                    if tasks_id.first_date == today:
                                        if task:
                                            template_id = self.env['ir.model.data']._xmlid_lookup(
                                                                                  'bi_all_in_one_project_management_system.email_template_edi_task_reminder')[2]
                                            email_template_obj = self.env['mail.template'].browse(template_id)
                                            if template_id:
                                                values = email_template_obj.generate_email(task.id, fields=['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                                                values['email_from'] = sus_id.email
                                                values['email_to'] = task.user_ids.email
                                                values['res_id'] = False
                                                values['author_id'] = self.env['res.users'].browse(request.env.uid).partner_id.id
                                                mail_mail_obj = self.env['mail.mail']
                                                msg_id = mail_mail_obj.sudo().create(values)
                                                if msg_id:
                                                    msg_id.sudo().send()

        return True



    @api.model
    def _cron_task_second_reminder(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        for task in self.env['project.task'].search([]):
            for tasks_id in self.env['res.config.settings'].search([],order="id desc", limit=1):
                if task.date_deadline !=False:
                    if task.reminder !=False:
                        reminder_date = datetime.strptime(str(task.date_deadline),'%Y-%m-%d').date()
                        today = datetime.now().date()
                        if tasks_id.second_date == today:
                            if tasks_id.second_date.month == today.month:
                                if tasks_id.second_date.day == today.day:
                                    if tasks_id.second_date == today:
                                        if task:
                                            template_id = self.env['ir.model.data']._xmlid_lookup(
                                                                                  'bi_all_in_one_project_management_system.email_template_edi_task_reminder')[2]
                                            email_template_obj = self.env['mail.template'].browse(template_id)
                                            if template_id:
                                                values = email_template_obj.generate_email(task.id, fields=['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                                                values['email_from'] = su_id.email
                                                values['email_to'] = task.user_ids.email
                                                values['res_id'] = False
                                                values['author_id'] = self.env['res.users'].browse(request.env.uid).partner_id.id
                                                mail_mail_obj = self.env['mail.mail']
                                                msg_id = mail_mail_obj.sudo().create(values)
                                                if msg_id:
                                                    msg_id.sudo().send()

        return True

    def _cron_post_deadline(self):
        for task in self.search([('is_task_done','=',False)]):
            schedule_task = '3 Tomorrow'

            today = date.today()
            next_day = today + timedelta(days=1)

            last_day_of_week = today + timedelta(days=5 - today.weekday())
            start_day_of_next_week = last_day_of_week + timedelta(days=1)
            last_day_of_next_week = start_day_of_next_week + timedelta(days=6)
            later_day = last_day_of_next_week + timedelta(days=1) 
            if task.date_deadline:
                if task.is_task_done:
                    schedule_task = '7 Done'
                elif task.date_deadline < today:
                    schedule_task = '1 Overdue'
                elif task.date_deadline == today:
                    schedule_task = '2 Today'
                elif task.date_deadline == next_day:
                    schedule_task = '3 Tomorrow'
                elif task.date_deadline > next_day and task.date_deadline <= last_day_of_week:
                    schedule_task = '4 This Week'
                elif task.date_deadline >= start_day_of_next_week and task.date_deadline <= last_day_of_next_week:
                    schedule_task = '5 Next Week'
                elif task.date_deadline > last_day_of_next_week:
                    schedule_task = '6 Later'

            task.update({
                'schedule_task' : schedule_task
            })

    def set_task_done(self):
        res = {}
        for task in self:
            if task.is_task_done == False:
                stage_id = self.env['project.task.type'].search([('project_ids','in',self.project_id.ids)],limit=1)

                task.write({
                    'is_task_done' : True,
                    'stage_id' : stage_id.id
                })
                task.message_post(body=_("The Task is Set to Done"))
            else:
                stage_id = self.env['project.task.type'].search([('name','=','New')])
                task.write({
                    'is_task_done' : False,
                    'stage_id' : stage_id.id
                })
                task.message_post(body=_("The Task is Set to New"))
            

    @api.depends('date_deadline','is_task_done')
    def check_schedule(self):
        for task in self:
            schedule_task = '3 Tomorrow'

            today = date.today()
            next_day = today + timedelta(days=1)

            last_day_of_week = today + timedelta(days=5 - today.weekday())
            start_day_of_next_week = last_day_of_week + timedelta(days=1)
            last_day_of_next_week = start_day_of_next_week + timedelta(days=6)
            later_day = last_day_of_next_week + timedelta(days=1) 
            if task.date_deadline:
                if task.is_task_done:
                    schedule_task = '7 Done'
                elif task.date_deadline < today:
                    schedule_task = '1 Overdue'
                elif task.date_deadline == today:
                    schedule_task = '2 Today'
                elif task.date_deadline == next_day:
                    schedule_task = '3 Tomorrow'
                elif task.date_deadline > next_day and task.date_deadline <= last_day_of_week:
                    schedule_task = '4 This Week'
                elif task.date_deadline >= start_day_of_next_week and task.date_deadline <= last_day_of_next_week:
                    schedule_task = '5 Next Week'
                elif task.date_deadline > last_day_of_next_week:
                    schedule_task = '6 Later'

            task.update({
                'schedule_task' : schedule_task
            })

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Good'),
        ('3', 'Excellent'),
    ], index=True, string="Priority");

    user_ids = fields.Many2many('res.users', relation='project_task_user_rel', column1='task_id', column2='user_id')
    task_completed = fields.Boolean(string="Task Completed")
    start_date = fields.Date(string='Start Date', index=True, copy=False, tracking=True)
    state_type_name = fields.Char('Status', related="stage_id.name")
    user_in_subtask = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    subtask_check = fields.Boolean(string="Subtask", default=False)
    subtask_count = fields.Integer(string='Count', compute='sub_task_found')

    done_stage_id = fields.Boolean('Is Done',default=False,store=True)
    todo_stage_id = fields.Boolean('Is ToDo',default=False,store=True)
    cancel_stage_id = fields.Boolean('Is Cancel',default=False,store=True)
    wiz_id = fields.Many2one('subtask.wizard', string="Wiz Parent Id")
    task_parent_id = fields.Many2one('project.task', string="Parent Id")
    subtask_ids = fields.One2many('project.task', 'task_parent_id', string="Subtask")
    des = fields.Char('Task Description')
    is_subtask = fields.Boolean('Is a subtask')
    task_stage = fields.Boolean(string='Task Completed',compute='check_task_completed')
    is_task_done = fields.Boolean(string='Task Done',default=False)
    schedule_task = fields.Selection([
        ('1 Overdue','Overdue'),
        ('2 Today','Today'),
        ('3 Tomorrow','Tomorrow'),
        ('4 This Week','This Week'),
        ('5 Next Week','Next Week'),
        ('6 Later','Later'),
        ('7 Done','Done')], default='3 Tomorrow', compute="check_schedule", store=True)
    meeting_id = fields.Many2one('calendar.event', string="Meeting", readonly=True)
    meeting_count = fields.Integer('Meeting',compute='_compute_meeting')
    seq3 = fields.Char('Number')
    order_id = fields.Many2one('sale.order', string="Sale Order")
    order_task_created = fields.Boolean(string='Order Task Created', default=False, copy=False)
    is_empty = fields.Boolean(string='Empty Task')
    task_product_ids = fields.Many2many('product.template',string='Products')
    task_product_id = fields.Many2one('product.template',string='Product')
    reminder = fields.Boolean(string='Reminder')
    task_Start = fields.Boolean(string='Task Start', default=False, readonly=True)
    end_time = fields.Datetime(
        string='End Date',
    )
    start_time = fields.Datetime(
        string='Start Date',
    )
    time_left = fields.Float(string='Real Timer')
    
    def start_task_button(self):
        allow_multi_task = self.env['ir.config_parameter'].sudo().get_param('bi_all_in_one_project_management_system.allow_multi_task')
        if allow_multi_task:
            self.start_time=datetime.now()
            self.task_Start= True
            
        else:
            check_task = self.env['project.task'].search([('task_Start', '=', 'True')],limit=1)
            if check_task:
                raise ValidationError(_('You can start only one task.....'))
            else:
                self.start_time=datetime.now()
                self.task_Start= True
                
    # count meeting
    @api.depends('meeting_id')
    def _compute_meeting(self):
        self.meeting_count = self.env['calendar.event'].search_count([('task_id','=',self.id)])
        
    @api.depends('stage_id')
    def check_task_completed(self):
        for rec in self:
            if rec.stage_id.task_completed == True:
                rec.task_stage = True
            else:
                rec.task_stage = False
                
    @api.onchange('stage_id')
    def _get_project_stage(self):
        if self.stage_id.name == 'Done':
            self.task_completed = True
        else:
            self.task_completed = False
        if self.project_id:
            for each in self.project_id.task_auto_assign_ids:
                if self.stage_id.id == each.stage_id.id and self.project_id.id == each.project_id.id:
                    self.user_ids = each.user_ids



    @api.model
    def _run_delay_deadline_notification(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        for task in self.env['project.task'].search([('date_deadline', '!=', None), ('user_ids', '!=', None),('stage_id','not in','Done'),('stage_id','not in','Cancelled')]):
            for tasks_id in self.env['res.config.settings'].sudo().search([],order="id desc", limit=1):
                count_day = tasks_id.delay_count
                reminder_date = task.date_deadline  + relativedelta(days=count_day)
                today = datetime.now().date()
                if reminder_date < today and tasks_id.delay_notification:
                    if task:
                            template_id = self.env['ir.model.data']._xmlid_lookup('bi_all_in_one_project_management_system.email_template_edi_remainder_delay_overdue_notification')[2]
                            email_template_obj = self.env['mail.template'].browse(template_id)
                            if template_id:
                                values = email_template_obj.generate_email(task.id, fields=['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to'])
                                values['email_from'] = su_id.email
                                values['res_id'] = False
                                values['author_id'] = self.env['res.users'].browse(request.env.uid).partner_id.id
                                mail_mail_obj = self.env['mail.mail']
                                msg_id = mail_mail_obj.sudo().create(values)
                                if msg_id:
                                    msg_id.sudo().send()
        return True


    @api.model
    def _run_delay_start_notification(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        for task in self.env['project.task'].search([('start_date', '!=', None),('stage_id','not in','In Progress'),('stage_id','not in','Done'),('stage_id','not in','Cancelled')]):
            for tasks_id in self.env['res.config.settings'].sudo().search([],order="id desc", limit=1):
                count_day = tasks_id.start_count
                reminder_date = task.start_date + relativedelta(days=count_day)
                today = datetime.now().date()
                if reminder_date < today and tasks_id.start_notification:
                    if task:
                        template_id = self.env['ir.model.data']._xmlid_lookup('bi_all_in_one_project_management_system.email_template_edi_remainder_delay_start_notification')[2]
                        email_template_obj = self.env['mail.template'].browse(template_id)
                        if template_id:
                            values = email_template_obj.generate_email(task.id, fields=['subject', 'body_html', 'email_from','email_to','partner_to', 'email_cc', 'reply_to'])
                            values['email_from'] = su_id.email
                            values['res_id'] = False
                            values['author_id'] = self.env['res.users'].browse(request.env.uid).partner_id.id
                            mail_mail_obj = self.env['mail.mail']
                            msg_id = mail_mail_obj.sudo().create(values)
                            if msg_id:
                                msg_id.sudo().send()
        return True

    @api.model
    def default_get(self, field_vals):
        res = super(Projecttask, self).default_get(field_vals);
        project = self.env["project.project"].browse(res.get("project_id",[]));
        if project:
            res["priority"] = project.priority
        current_stage = self._context.get('default_stage_id')
        current_project = self._context.get('default_project_id')
        project = self.env['project.project'].search([('id', '=', current_project)])
        project_stage_ids = self.env['project.task.type'].search([('dft_for_new_project', '=', True)])
        if project_stage_ids:
            for rec in project_stage_ids:
                if rec.id == current_stage:
                    res.update({'user_ids': [(4, rec.dft_assign_user_id.id)]})

        if project.task_auto_assign_ids:
            for stage in project.task_auto_assign_ids:
                if stage.stage_id.id == current_stage:
                    res.update({'user_ids': [(4, stage.user_ids.id)]})
        else:
            pass
        team_id = self.env.user.team_id
        project_id = team_id.order_project_id and team_id.order_project_id.id or False

        date = fields.Date.context_today(self)

        date_deadline = date + relativedelta(days=1)

        res.update({
            'project_id' : project_id,
            'date_deadline' : date_deadline
        })

        return res
    
    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False
        template_id = self.env['ir.model.data']._xmlid_to_res_id('bi_all_in_one_project_management_system.mail_template_task', raise_if_not_found=False)
        return template_id


    def action_send_task(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        attachments = self.env['ir.attachment'].search([('res_model','=','project.task'),('res_id','=',self.id)])
        attachments_ids=[]
        for attachment in attachments:
            attachments_ids.append(attachment.id)
        ctx = {
            'default_model': 'project.task',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_attachment_ids': ([(6,0,attachments_ids)]),
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    
    @api.depends('wiz_id.subtask_lines')
    def sub_task_found(self):
        for each in self:
            each.subtask_count = len(each.subtask_ids)
    
    def action_done(self):
        for each in self:
            done_stage_search = self.env['res.config.settings'].search([], limit=1, order="id desc").done_stage_ckecklist
            if not done_stage_search:
                raise UserError('You can not move stage, Please Configure Done stage.')
            else:
                each.write({'stage_id' : done_stage_search.id,'done_stage_id' : True,'todo_stage_id' : False}) 
                
    def action_cancel(self):
        for each in self:
            cancel_stage_search = self.env['res.config.settings'].search([], limit=1, order="id desc").cancel_stage_ckecklist
            if not cancel_stage_search:
                raise UserError('You can not move stage, Please Configure Cancel stage.')
            else:
                each.write({'stage_id' : cancel_stage_search.id,'cancel_stage_id' : True})
            
    def action_todo(self):
        for each in self:
            todo_stage_search = self.env['res.config.settings'].search([], limit=1, order="id desc").todo_stage_ckecklist
            if not todo_stage_search:
                raise UserError('You can not move stage, Please To Do stage.')
            else:
                each.write({'stage_id' : todo_stage_search.id, 'todo_stage_id' : True,'done_stage_id' : False})
            
    @api.model
    def create(self, vals):
        combine_seq = self.env['ir.sequence'].next_by_code('project.task') or _('New')
        vals.update({'seq3':combine_seq})
        rec = super(Projecttask, self).create(vals)
        for p_task in self:
            for task in p_task.subtask_ids:
                if task.state_type_name:
                    msg = task.state_type_name + ':' + task.name
                else:
                    msg = task.name

                p_task.message_post(body=msg)
        return rec
    
    def write(self, vals):
        old_ids = []
        if 'project_id' in vals:
            project = vals.get('project_id')
            project_id = self.env['project.project'].browse(project)
            task_sq_code = project_id.task_sequence_id.code
            if project_id.seq2 and project_id.task_sequence_id:
                combine_seq = project_id.seq2 + "/" + str(self.env['ir.sequence'].next_by_code(task_sq_code))
            else:
                combine_seq = self.env['ir.sequence'].next_by_code('project.task') or _('New')
            vals.update({'seq3': combine_seq})
        for p_task in self:
            for task in p_task.subtask_ids:
                if task.state_type_name:
                    msg = task.state_type_name + ':' + task.name
                else:
                    msg = task.name

                p_task.message_post(body=msg)
            for j in p_task.tag_ids:
                old_ids.append(j.name)
        res = super(Projecttask, self).write(vals)
        for obj in self:
            new_ids = []
            if vals.get('tag_ids', False):
                all_ids = vals.get('tag_ids')
                if all_ids[0][1] == False:
                    for i in all_ids[0][2]:
                        tag_obj = self.env['project.tags'].search([('id', '=', i)]).name
                        new_ids.append(tag_obj)

                    final_new = str(new_ids)[1:-1]
                    final_old = str(old_ids)[1:-1]

                    obj.message_post(body=_("Tags added: <b> %s </b>  --> <b> %s </b>") % (final_old, final_new))
                else:
                    for i in all_ids:
                        tag_obj = self.env['project.tags'].search([('id', '=', i[1])]).name
                        new_ids.append(tag_obj)

                    final_new = str(new_ids)[1:-1]
                    final_old = str(old_ids)[1:-1]

                    obj.message_post(body=_("Tags added: <b> %s </b>  --> <b> %s </b>") % (final_old, final_new))
        if vals.get('stage_id'):
            task_type_search = self.env['res.config.settings'].search([], limit=1, order="id desc").warning_child_task
            if task_type_search:
                if vals.get('stage_id') == task_type_search.id:
                    for task in self.subtask_ids:
                        if task.stage_id.id != task_type_search.id:
                            raise UserError("You can not close parent task until all child tasks are closed.")
            stage_name = self.env['project.task.type'].browse(vals.get('stage_id')).name
            if self.is_task_done == False:
                vals.update({
                    'kanban_state' : 'done'
                })
            else:
                vals.update({
                    'kanban_state' : 'normal'
                }) 

            if stage_name in ['Archive']:
                vals.update({
                        'active':False
                    })
        if vals.get('task_product_id'):
            new_task_product_id = self.env['product.template'].browse(int(vals.get('task_product_id')))
            old_task_product_id = self.task_product_id

            new_task_product_id.write({
                'task_ids' : [(4, self.id)],
                'project_id' : self.project_id.id
            })

            if old_task_product_id:
                old_task_product_id.write({
                    'task_ids' : [(3, self.id)],
                })
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        rec = super(Projecttask, self).copy(default)
        return rec

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'project.task', 'default_res_id': self.id}
        return res

    
    def duplicate_task(self):
        for task in self:
            task.copy(default={
                'name' : task.name + ' (Copy)',
                'order_id' : task.order_id.id,
                'stage_id' : task.stage_id and task.stage_id.id,
            })

    @api.onchange('parent_id')
    def button_disable(self):
        if self.parent_id:
            self.is_subtask = True
            self.task_parent_id = self.parent_id.id
            self.project_id = self.parent_id.project_id
        else:
            self.is_subtask = False
            self.task_parent_id = self.id
            self.project_id = False


    def _compute_subtask_count(self):
        for task in self:
            task_ids = self.env['project.task'].search([('task_parent_id', '=', task.id)])
            task.subtask_count = len(task_ids)
            self.parent_id = task.task_parent_id

    
class subtask_wizard(models.Model):
    _name = 'subtask.wizard'
    _description = "Subtask Wizard"

    subtask_lines = fields.One2many('project.task', 'wiz_id', string="Task Line")

    def create_subtask(self):
        list_of_stage = []
        project_task_id = self.env['project.task'].browse(self._context.get('active_id'))

        for stage in project_task_id.project_id.type_ids:
            stage_ids = self.env['project.task.type'].search([('id', '=', stage.id)])
            list_of_stage.append(stage_ids.id)
        for task in self.subtask_lines:
            task.task_parent_id = self._context.get('active_id')
            task.description = task.des
            task.is_subtask = True
            # NOTE :- its is added in odoo 16 , so in older versions this is needed but not in 16
            # if list_of_stage:
            #     task.stage_id = list_of_stage[0]
            task.project_id = project_task_id.project_id.id
            task.subtask_check = True
            msg = task.state_type_name or ' ' + ' ' + ':' + ' ' + task.name
            task.task_parent_id.message_post(body=msg)
        return True
    



class ProjectTaskType(models.Model):
    _inherit= 'project.task.type'


    task_completed = fields.Boolean(string='Task Completed')
    dft_assign_user_id = fields.Many2one('res.users', string="Default Assigned User")
    dft_for_new_project = fields.Boolean(string="Default for New Project")



class Project(models.Model):
    _inherit = 'project.project'


    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Good'),
        ('3', 'Excellent'),
    ], index=True, string="Priority")

    @api.onchange('priority')
    def onchange_priority(self):
        project_task = self.env['project.task'].search([('project_id','in',self.ids)]);
        for i in project_task:
            i.priority=self.priority
            


class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    end_time = fields.Datetime(
        string='End Date',
    )
    start_time = fields.Datetime(
        string='Start Date',
    )



class Calculate_time(models.TransientModel):
    _name = 'project.task.timer.wizard'


    description=fields.Char(string='Description')

    end_time = fields.Datetime(string='End Date', readonly=True)
    start_time = fields.Datetime(string='Start Date', readonly=True)
    duration = fields.Float(string='Duration',readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(Calculate_time, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        current_task_id = self.env['project.task'].browse(active_ids[0])

        diff = datetime.now() - current_task_id.start_time 
        diff_in_hours = diff.total_seconds() / 3600
        res['start_time']= current_task_id.start_time
        res['end_time']=datetime.now()
        res['duration']=float(diff_in_hours)

        return res

    
    def end_task_kanban(self):

        active_ids = self.env.context.get('active_ids')
        current_task_id = self.env['project.task'].browse(active_ids)
        for data in current_task_id:
            project_id = data.project_id.id
            task_id = data.id
            data.task_Start=False
  
        timesheet = self.env['account.analytic.line']
        vals = {
            'date':self.start_time,
            'name':self.description,
            'project_id':project_id,
            'task_id':task_id,
            'unit_amount' : self.duration,
            'end_time' : self.end_time,
            }
        
        res = timesheet.create(vals)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload', 
            }

    def end_task(self):

        active_ids = self.env.context.get('active_ids')
        current_task_id = self.env['project.task'].browse(active_ids)
        for data in current_task_id:
            project_id = data.project_id.id
            task_id = data.id
            data.task_Start=False
  
        timesheet = self.env['account.analytic.line']
        vals = {
            'date':self.start_time,
            'name':self.description,
            'project_id':project_id,
            'task_id':task_id,
            'unit_amount' : self.duration,
            'end_time' : self.end_time,
            }

        res = timesheet.create(vals)
        
        return res


  
