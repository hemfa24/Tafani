# -*- coding: utf-8 -*-
{
    'name': 'Hemfa Employee Attendance Report Custom',
    'summary': " 629_hr_attendance_summary_report_custom_R_S_r16.0.1.0_4-6-2023  ttandance sheet custom in report",
    'description': "Employee Attendance Report",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Human Resources',
    'version': '14.0.0.1.0',
    'depends': ['hr_attendance_summary_report','hr_shifts_custom'],

    'data': [
        # 'security/ir.model.access.csv',
        'report/hr_attendance_report_view.xml',
        # 'wizard/hr_attendance_report_wizard.xml',
    ],

    'license': "OPL-1",
}
