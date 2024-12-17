# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Project Tasks',
    'version': '16.0.0.1',
    "category": "Human Resources",
    'license':'OPL-1',
    'summary': 'This module helps to display assinged task to Employee form and kanban view',
    "description": """
        This module helps to display assinged task to Employee, employee tasks, tasks employee,visible tasks on employee. Tasks list on employee,
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends':['base','hr','project'],
    'data':[
        'views/employee_task.xml',
        'security/employee_security.xml',
        ],
    'installable': True,
    'auto_install': False,
    "live_test_url":'https://youtu.be/hW7tdOYQrY4',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

