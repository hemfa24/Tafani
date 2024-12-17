from odoo import fields, models,api,_
import time,os
from datetime import datetime, timedelta
from odoo.exceptions import Warning as UserError
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
import pytz

class HR_Attendance_sheet_notify_Custom(models.Model):
    _inherit = 'attendance.sheet'
    # _inherits=[]
    def action_attsheet_confirm(self):
        for att_sheet in self:
            if att_sheet.att_sheet_line_ids:
                for att in att_sheet.att_sheet_line_ids:
                    if att.hr_action=='validate':
                        raise ValidationError(_('Please validate attendance records before submit to manager!'))
            for att in att_sheet.att_sheet_line_ids:
                att_sheet.correct_att_sheet_line_ids = [(0, 0, {
                                    'date': att.date,
                                    'day': att.day,
                                    'pl_sign_in':att.pl_sign_in,
                                    'pl_sign_out':att.pl_sign_out,
                                    'ac_sign_in': att.ac_sign_in,
                                    'ac_sign_out': att.ac_sign_in,
                                    'act_late_in':att.act_late_in,
                                    'act_diff_time':att.act_diff_time,
                                    'late_in':0,
                                    'diff_time':0,
                                    'overtime': att.overtime,
                                    'att_sheet_id': att.att_sheet_id.id,
                                    'line_att_policy_id':att.line_att_policy_id.id,
                                    'status': att.status,
                                    'hr_action': att.hr_action,
                                    'note': ''
                                })]
                
            att_sheet.calculate_att_data()
            att_sheet.write({'state': 'confirm'})
        manager_id=False
        if self.employee_id.parent_id.user_id:
            manager_id=self.employee_id.parent_id.user_id
            self.activity_schedule('hr_notify_custom.attendance.sheet',user_id=manager_id.id, note=f'You have pending attendance sheet action(self.name)')
    
