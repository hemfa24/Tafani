# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import logging

class attendanceWizardReport(models.AbstractModel):
    _name = 'report.hr_attendance_summary_report.employee_attendance_view'
    _description = 'Account report with payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'hr_attendance_summary_report.employee_attendance_view')
        s_date = datetime.strptime(data['from_date'], DEFAULT_SERVER_DATE_FORMAT).date()
        e_date = datetime.strptime(data['to_date'], DEFAULT_SERVER_DATE_FORMAT).date()
        delta = e_date - s_date
        days = []
        dateofday = []
        weekdays = []
        for i in range(delta.days + 1):
            day = s_date + timedelta(days=i)
            date_of_day = day.day
            dateofday.append(date_of_day)
            days.append(day)
            weekdays.append(day.strftime("%a"))
        status_dict = {}
        dept_dict = {}
        time_dict = {}
        employees = self.env['hr.employee'].search([])
        if data['select_type'] == 'employee':
            if data['employee_id'] :
                employees = self.env['hr.employee'].search([('id', 'in', data['employee_id'])])
        else:
            if data['department_id']:
                employees = self.env['hr.employee'].search([('department_id', 'in', data['department_id'])])
        for employee_id in employees:
            day_working_hour = employee_id.resource_calendar_id.hours_per_day / 2
            employee_attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee_id.id), ('check_in', '>=', data['from_date']), ('check_in', '<=', data['to_date'])])
            status = []
            hour = []
            date_list={}
            working_day = []
            for day in days:
                date = day.strftime('%Y-%m-%d %H:%M:%S')
                match_shift=self.env['zk.machine'].get_match_shift(str(date),employee_id.id)
                date = day.strftime('%Y-%m-%d')
                is_absent=True
                for attendance in employee_attendance:
                    check_in_date = attendance.check_in.date()
                    day_index = days.index(day)
                    if str(attendance.check_in.date())==str(date):
                        if str(attendance.check_in.date()) in date_list:
                            continue

                        if str(attendance.check_in.date()) not in date_list:
                            date_list[str(attendance.check_in.date())]=0
                        is_absent=False
                        worked_hour=attendance.worked_hours
                        if attendance.check_out=='':
                            status.append('PF')
                        else:
                            if attendance.check_in=='':
                                status.append('LF')
                            else:
                                status.append('P')
                        hour.append(worked_hour)
                        
                if is_absent:
                    in_leave=self.env['hr.leave'].search([('holiday_type','=','employee'),
                            ('employee_id','=',employee_id.id),
                            ('request_date_from','<=',date),
                            ('request_date_to','>=',date),
                            ('state','=','validate')])
                    avg_hours=0
                    if match_shift:
                        avg_hours=match_shift.schedule_id.hours_per_day
                    

                    if in_leave:
                        status.append('L')                        
                        hour.append(avg_hours)
                    else:                       
                        c_date=datetime(day.year,day.month,day.day)
                        ph_leaves=self.env['attendance.sheet'].get_public_holiday2(c_date.date(),employee_id)
                        if ph_leaves:
                            status.append('PH')
                            hour.append(avg_hours)
                        else:
                            if match_shift:
                                if match_shift.hr_shift.day_period=='rest':
                                    status.append(' ')
                                    hour.append(0)
                                    continue
                                if match_shift.hr_shift.day_period=='weekend':
                                    status.append('W')
                                    hour.append(0)
                                    continue
                            status.append('A')
                            hour.append(0)
            time_dict.update({employee_id.name: hour})
            status_dict.update({employee_id.name: status})
            dept_dict.update({employee_id.name: employee_id.department_id.name})

        return {

            'doc_ids': self.ids,
            'doc_model': report.model,
            'report_options': data['report_options'],
            'from_date': data['from_date'],
            'to_date': data['to_date'],
            'day': dateofday,
            'weekday': weekdays,
            'status_dict': status_dict,
            'dept_dict': dept_dict,
            'time_dict': time_dict,

        }
