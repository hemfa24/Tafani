# -*- coding: utf-8 -*-

{
    'name' : 'Employee Overtime Request',
    'author': "Mahmoud Kousa",
    'version' : '16.0.1.0',
    'summary' : 'Employee overtime request employee overtime approval overtime with payroll',
    'description' : """
    Python Code Rule:
        result = payslip.overtime_wages
    """,
    'depends' : ['hr','hr_payroll_community'],
    "license" : "OPL-1",
    'data': [
        'data/sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/refuse_request_wizard_view.xml',
        'views/hr_overtime_view.xml',
        'views/hr_payroll_view.xml',
        'views/resource_view.xml',
            ],
    'qweb' : [],
    'demo' : [],
    'installable' : True,
    'auto_install' : False,
    'category' : 'Human Resources',
}
