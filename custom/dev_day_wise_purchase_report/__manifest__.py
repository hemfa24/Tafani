# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Day Wise Purchase Report | Purchase day wise | Purchase day book | Day Wise Report | Purchase Daily Report | Purchase Report | Purchase',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Purchases',
    'description':
        """
 This Module add below functionality into odoo
        

        1.print day wise sale report \n

day wise product Purchase report
odoo day wise product Purchase report
odoo day wise report 
odoo day wise product report 
odoo day wise product Purchase report 

odoo application will print day wise product purchase report, day waise report, purchase daybook, purchase daywise, purchase daily report, daily purchase, daily product purchase, product daybook purchase, purchase day book , purchase day report

    """,
    'summary': 'odoo application will print day wise product purchase report, day waise report, purchase daybook, purchase daywise, purchase daily report, daily purchase, daily product purchase, product daybook purchase, purchase day book , purchase day report',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_days_wizard.xml',
        'report/purchase_days_report_template.xml',
        'report/purchase_days_menu.xml',
        
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':15.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'license': 'LGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
