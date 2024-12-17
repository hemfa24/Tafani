# -*- coding: utf-8 -*-
{
    'name': 'Project and Task Report in Odoo',
    "author": "Edge Technologies",
    'version': '16.0.1.0',
    'live_test_url': "https://youtu.be/RGymMBdvNhw",
    "images":['static/description/main_screenshot.png'],
    'summary': "Print Project and Task Report Using Different Filter Project Task Reports Tasks Print Project Task Report Project Task PDF Report Print PDF Report On Project and Task Print PDF Report Task Project Report Task PDF Report Task Reports Project Task",
    'description': """This App helps User to Print Project and Task Report Between Start Date and End Date Using Different Filter Like User of Project or Task and Task Stage.
    
Project Task Repots
Reports in Project Report on Tasks Print Project Task Report Project And Task PDF Report
print PDF report on project and task print PDF report task Project Report XLS & PDF Project task Report XLS & PDF
task pdf report, task reports Project Task Report project reports
project pdf reports project task pdf reports 




    """,
    "license" : "OPL-1",
    'depends': ['base','project','hr_timesheet'],
    'data': [
            "security/ir.model.access.csv",
            "views/project_task_report_view.xml",
            "views/project_report_template.xml",
            "views/project_task_report_template.xml",
            ],
    'installable': True,
    'auto_install': False,
    'price': 000,
    'currency': "EUR",
    'category': 'Project',

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
