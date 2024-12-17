# -*- coding: utf-8 -*-
{
    'name': 'Employee Attendance Report',
    'summary': "610_hr_attendance_summary_report_R_S_R16.0.0.1.1_4-6-2023 Print employee attendance Report with status & hours on date range",
    'description': "Print employee attendance Report with status & hours on date range",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Human Resources',
    'version': '16.0.0.1.1',
    'depends': ['hr_attendance'],

    'data': [
        'security/ir.model.access.csv',
        'report/hr_attendance_report_view.xml',
        'wizard/hr_attendance_report_wizard.xml',
    ],

    'license': "OPL-1",
    'price': 30,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_check',
}
