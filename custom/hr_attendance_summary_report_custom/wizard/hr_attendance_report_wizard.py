# -*- coding: utf-8 -*-

from odoo import models, fields,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DT
import logging
import xlwt
import io
import base64
import pytz

class hrAttendanceReport_Custom(models.TransientModel):
	_inherit = "hr.attendance.report.wizard"
	_description = "HR Attendance Report wizard"
	select_type = fields.Selection([
        ('employee', 'Employees'),
        ('department', 'Department')], string="Print report by", default="employee")
	department_id = fields.Many2many('hr.department', string="Department")
	def attendance_report(self):
		data = {
			'model': 'hr.attendance',
			'from_date': self.from_date,
			'to_date': self.to_date,
			'employee_id': self.employee_id.ids,
			'department_id': self.department_id.ids,
			'report_options': self.report_options,
			'select_type': self.select_type,
		}
		return self.env.ref('hr_attendance_summary_report.report_employee_attendance').report_action(self, data=data)
	def get_employee_attendance(self):
		report = self.env['ir.actions.report']._get_report_from_name(
			'hr_attendance_summary_report.employee_attendance_view')
		s_date = self.from_date
		e_date = self.to_date
		delta = e_date - s_date
		days = []
		dateofday = []
		weekdays = []
		data_list = []
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
		if self.select_type == 'employee':
			if self.employee_id :
				employees = self.env['hr.employee'].search([('id', 'in', self.employee_id.ids)])
		else:
			if self.department_id:
				employees = self.env['hr.employee'].search([('department_id', 'in', self.department_id.ids)])
		
		for employee_id in employees:
			employee_attendance = self.env['hr.attendance'].search(
				[('employee_id', '=', employee_id.id), ('check_in', '>=', self.from_date), ('check_in', '<=', self.to_date)])
			
			status = []
			hour = []
			working_day = []
			date_list={}
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
			'report_options': self.report_options,
			'from_date': self.from_date,
			'to_date': self.to_date,
			'day': dateofday,
			'weekday': weekdays,
			'status_dict': status_dict,
			'dept_dict': dept_dict,
			'time_dict': time_dict,

		}
	def export_excel(self):
		data = self.get_employee_attendance()
		from_date = data.get('from_date').strftime(DT)
		to_date = data.get('to_date').strftime(DT)
		
		# --- Workbook / filename / header / subheader --- #
		workbook = xlwt.Workbook()
		filename = 'Hr Attendance Report.xls'
		worksheet = workbook.add_sheet('Hr Attendance Report')
		header = xlwt.easyxf(
			'font: bold 1,height 200;'
			'pattern: pattern_fore_colour blue;'
			'align: vertical center, horizontal center, wrap on;'
			)
		sub_red = xlwt.easyxf(
            "pattern: pattern solid, pattern_fore_colour red; font: bold 1;"
            'align: vertical center, horizontal center, wrap on;')
		sub_green = xlwt.easyxf(
            "pattern: pattern solid, pattern_fore_colour green; font: bold 1;"
            'align: vertical center, horizontal center, wrap on;')
		sub_blue = xlwt.easyxf(
            "pattern: pattern solid, pattern_fore_colour blue; font: bold 1;"
            'align: vertical center, horizontal center, wrap on;')
		sub_yellow = xlwt.easyxf(
            "pattern: pattern solid, pattern_fore_colour yellow; font: bold 1;"
            'align: vertical center, horizontal center, wrap on;')
		sub_gray = xlwt.easyxf(
            "pattern: pattern solid, pattern_fore_colour gray25; font: bold 1;"
            'align: vertical center, horizontal center, wrap on;')
		
		worksheet.col(0).width = 5500
		worksheet.col(1).width = 5500
		for i in range(2,35):
			worksheet.col(i).width = 1500
		
		# -----  Worksheet -------- #
		worksheet.write_merge(0, 1, 12, 19, _('Employee Attendance Summary Report'), header)
		worksheet.write_merge(2, 2, 0, 4, _('From: ') + from_date +' '+_('To: ')+ to_date, header)
		row = 3
		col = 0
		worksheet.write_merge(row, row+1, col, col, _('Employee'), header)
		worksheet.write_merge(row, row+1, col+1, col+1, _('Department'), header)
		col += 1
		for day in data.get('day'):
			col += 1
			worksheet.write(row , col , day, header)
		col = 1
		col_total = len(data.get('day')) 
		for weekday in data.get('weekday'):
			col += 1
			worksheet.write(row+1, col, weekday, header)
		if data.get('report_options') == 'summary':
			worksheet.write_merge(row, row+1, col_total+2, col_total+3, _('Total Present'), header)
			worksheet.write_merge(row, row+1, col_total+4, col_total+5, _('Total Absent'), header)
		else:
			worksheet.write_merge(row, row+1, col_total+2, col_total+3, _('Total Hour'), header)
		row = 4
		col = 0
		if data.get('report_options') != 'Summary_with_horurs':
			logging.info(">>>>>>>>status="+str(data.get('status_dict')))
			for employee in data.get('status_dict'):
				row += 1
				worksheet.write(row, 0, employee, header)
				worksheet.write(row, 1, data.get('dept_dict')[employee], header)
				count = 0
				countA = 0
				col = 1
				for status in data.get('status_dict').get(employee):
					col += 1
					if status == 'A':
						worksheet.write(row, col, status, sub_red)
						countA = countA + 1
					elif status == 'P':
						count = count + 1
						worksheet.write(row, col, status, sub_green)
					elif status == 'L':
						worksheet.write(row, col, status, sub_blue)
					elif status == 'PH':
						worksheet.write(row, col, status, sub_yellow)
					else:
						worksheet.write(row, col, status, sub_gray)
					# if col == len(data.get('status_dict').get(employee)):
					# 	col = 1
				worksheet.write_merge(row, row, col_total + 2, col_total + 3, count, header)
				worksheet.write_merge(row, row, col_total + 4, col_total + 5, countA, header)
		else:
			for employee in data.get('status_dict'):
				row += 1
				worksheet.write_merge(row, row+1, 0, 0, employee, header)
				worksheet.write_merge(row, row+1, 1, 1, data.get('dept_dict')[employee], header)
				col = 1
				for status in data.get('status_dict').get(employee):
					col += 1
					if status == 'A':
						worksheet.write(row, col, status, sub_red)
					elif status == 'P':
						worksheet.write(row, col, status, sub_green)
					elif status == 'L':
						worksheet.write(row, col, status, sub_blue)
					elif status == 'PH':
						worksheet.write(row, col, status, sub_yellow)
					else:
						worksheet.write(row, col, status, sub_gray)
					# if col == len(data.get('status_dict').get(employee)):
					# 	col = 0
				row += 1
				col=1
				total_time = []
				for time in data.get('time_dict').get(employee):
					col += 1
					total_time.append(time)
					worksheet.write(row, col, time, header)
					# if col == len(data.get('time_dict').get(employee)):
					# 	col = 0
				row -= 1
				worksheet.write_merge(row, row+1, col_total+3, col_total+4, sum(total_time), header)

				row +=1
		# worksheet.write_merge(row+2, row+3,  1,  8, _('Color Key Map'), header)
		# worksheet.write_merge(row+4, row+4,  1,  1, _('Color'), header)
		# worksheet.write_merge(row+4, row+4,  2,  4, _('Description'), header)
		# worksheet.write_merge(row+4, row+4,  5,  5, _('Color'), header)
		# worksheet.write_merge(row+4, row+4,  6,  8, _('Description'), header)

		# worksheet.write_merge(row+5, row+5,  1,  1, 'A', sub_red)
		# worksheet.write_merge(row+5, row+5,  2,  4, _('Absent'), header)
		# worksheet.write_merge(row+5, row+5,  5,  5, 'p', sub_green)
		# worksheet.write_merge(row+5, row+5,  6,  8, _('Present'), header)

		
		# worksheet.write_merge(row+6, row+6,  1,  1, 'PH', sub_yellow)
		# worksheet.write_merge(row+6, row+6,  2,  4, _('Public Holiday'), header)
		# worksheet.write_merge(row+6, row+6,  5,  5, 'L', sub_blue)
		# worksheet.write_merge(row+6, row+6,  6,  8, _('Leave'), header)

		# worksheet.write_merge(row+7, row+7,  1, col + 1, 'W', sub_gray)
		# worksheet.write_merge(row+7, row+7,  2, col + 4, _('Weekend'), header)
		# worksheet.write_merge(row+7, row+7,  5, col + 5, ' ', sub_gray)
		# worksheet.write_merge(row+7, row+7,  6, col + 8, _('Rest'), header)

		# ------ return to excel ------#
		fp = io.BytesIO()
		workbook.save(fp)
		report_id = self.env['generate.excel.report'].create({
			'file': base64.encodebytes(fp.getvalue()),
			'file_name': filename})
		fp.close()
		return {
				'url': '/web/binary/download_excel_report/%s' % report_id.id,
				'type': 'ir.actions.act_url',
				'target': 'self'
		}
