# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name':'Print Asset Report',
    'version':'4.2.1',
    'currency': 'EUR',
    'category' : 'Accounting & Finance',
    'license': 'Other proprietary',
    'images': ['static/description/asset3.png'],
    'price': 10.0,
    'summary': 'Print Asset PDF Report',
    'description': """
                Asset Print Report
                Print Asset 
                Asset Report
            """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'live_test_url':'https://probuseappdemo.com/probuse_apps/asset_print_report/613',
    'depends': ['odoo_account_asset'],
    'data':['report/asset_print_report.xml'
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

