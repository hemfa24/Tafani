# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Loans and Advance Custom',
    'version': '16.0.1.6',
    'category': 'Productivity/Notes',
    'description': """
This module update Shifts module
=================================================================

Use for update hr_employee_shift module to add new features.

""",
    'summary': '627_oh_advance_salary_custom_R_S_R16.0.1.0_4-6-2023  salary advance rule , Fix Loading error when approve advance salary',
    'depends': [
        'ohrms_salary_advance',
        'hr_shifts_custom',
        'base'
    ],
    'data': [ 
        'security/ir.model.access.csv',
 
        'views/salary_advance_custom_view.xml',
        'views/menus.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
