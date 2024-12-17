# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Timesheets on CRM Pipeline/Opportunity',
    'version': '6.2.2',
    'price': 15.0,
    'category' : 'Sales/CRM',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """CRM Pipeline / CRM Opportunity Form with Timesheets""",
    'description': """
CRM Pipeline / CRM Opportunity Form with Timesheets
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_timesheets_odoo/701',#'https://youtu.be/dZtsEe9mL8E',
    'images': [
        'static/description/cp.png'
    ],
    'depends': [
        'crm',
        'hr_timesheet',
    ],
    'data':[
        'views/crm_lead_views.xml',
        'views/hr_timesheet_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
