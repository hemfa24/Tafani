# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta

import logging
class attendanceWizardReportcustom(models.AbstractModel):
    _inherit = 'report.hr_attendance_summary_report.employee_attendance_view'
    

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
        time_dict = {}
        employees = self.env['hr.employee'].search([])
        if data['employee_id']:
            employees = self.env['hr.employee'].search([('id', 'in', data['employee_id'])])
        for employee_id in employees:
            day_working_hour = employee_id.resource_calendar_id.hours_per_day / 2
            employee_attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee_id.id), ('check_in', '>=', data['from_date']), ('check_in', '<=', data['to_date'])],order="check_in")
            
            status = []
            hour = []
            working_day = []
            for day in days:
                attendance_ids = employee_id.resource_calendar_id.attendance_ids
                global_leave_ids = employee_id.resource_calendar_id.global_leave_ids
                for attendance_id in attendance_ids:
                    day_of_week = dict(
                        attendance_ids._fields['dayofweek'].selection).get(attendance_id.dayofweek)
                    if not day_of_week in working_day:
                        working_day.append(day_of_week)
                global_leave_lst = []
                for global_leave in global_leave_ids:
                    global_leave_date = global_leave.date_to.date() - global_leave.date_from.date()
                    for i in range(global_leave_date.days + 1):
                        globale_date = global_leave.date_from.date() + timedelta(days=i)
                        global_leave_lst.append(globale_date)
                
                if day.strftime("%A") not in working_day:
                    status.append(' ')
                elif day in global_leave_lst:
                    status.append('H')
                else:
                    status.append('A')

                hour.append(0)
                worked_hour=0
                for attendance in employee_attendance:
                    check_in_date = attendance.check_in.date()
                    if attendance.check_out:
                        
                        if check_in_date == day and check_in_date not in global_leave_lst:
                            worked_hour+=attendance.worked_hours
                            if check_in_date == day:
                                day_index = days.index(day)
                                hour[day_index] = worked_hour

                                if hour[day_index] <= day_working_hour:
                                    status[day_index] = 'H/F'
                                else:
                                    status[day_index] = 'P'
                        else:
                            if check_in_date == day:
                                day_index = days.index(day)
                                if hour[day_index] == 0:
                                    hour[day_index] = worked_hour
                                else:
                                    hour[day_index] = worked_hour + worked_hour
            time_dict.update({employee_id.name: hour})
            status_dict.update({employee_id.name: status})

        return {

            'doc_ids': self.ids,
            'doc_model': report.model,
            'report_options': data['report_options'],
            'from_date': data['from_date'],
            'to_date': data['to_date'],
            'day': dateofday,
            'weekday': weekdays,
            'status_dict': status_dict,
            'time_dict': time_dict,

        }
