# -*- coding: utf-8 -*-
import datetime
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


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
        time_dict = {}
        employees = self.env['hr.employee'].search([])
        if data['employee_id']:
            employees = self.env['hr.employee'].search([('id', 'in', data['employee_id'])])
        for employee_id in employees:
            day_working_hour = employee_id.resource_calendar_id.hours_per_day / 2
            employee_attendance = self.env['hr.attendance'].search(
                [('employee_id', '=', employee_id.id), ('check_in', '>=', data['from_date']), ('check_in', '<=', data['to_date'])])
            status = []
            hour = []
            working_day = []
            for day in days:
                attendance_ids = employee_id.resource_calendar_id.attendance_ids
                global_leave_ids = employee_id.resource_calendar_id.global_leave_ids
                for attendance_id in attendance_ids:
                    day_of_week = dict(
                        attendance_ids._fields['dayofweek'].selection).get(attendance_id.dayofweek)
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
                    hr_holidays = self.env['ir.module.module'].sudo().search([('name', '=', 'hr_holidays'), ('state', '=', 'installed')])
                    leave_id = False
                    if hr_holidays:
                        leave_id = self.env['hr.leave'].sudo().search([
                            ('employee_id', 'in', employee_id.ids),
                            ('date_from', '<=', day),
                            ('date_to', '>=', day),
                            ('state', '=', 'validate')
                        ])
                    if leave_id:
                        status.append('L')
                    else:
                        status.append('A')

                hour.append(0)
                for attendance in employee_attendance:
                    check_in_date = attendance.check_in.date()
                    if attendance.check_out:
                        delta_hour = attendance.check_out - attendance.check_in
                        worked_hour = str(delta_hour.total_seconds() / 3600.0)
                        asplit = worked_hour.split('.')
                        # worked_hour = round(float(asplit[0] + '.' + str(int(float(asplit[1]) * 60))), 2)
                        if check_in_date.strftime("%A") in working_day and check_in_date not in global_leave_lst:
                            if check_in_date == day:
                                day_index = days.index(day)
                                if hour[day_index] == 0:
                                    hour[day_index] = float(worked_hour)
                                else:
                                    hour[day_index] += float(worked_hour)

                                if hour[day_index] <= day_working_hour:
                                    status[day_index] = 'H/F'
                                else:
                                    status[day_index] = 'P'
                        else:
                            if check_in_date == day:
                                day_index = days.index(day)
                                if hour[day_index] == 0:
                                    hour[day_index] = float(worked_hour)
                                else:
                                    hour[day_index] += float(worked_hour)
            total_hour = sum(h for h in hour)
            hour.append(total_hour)
            time_dict.update({employee_id.name: [str(timedelta(hours=h)).rsplit(':', 1)[0] for h in hour]})
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
