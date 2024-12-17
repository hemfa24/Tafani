# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Asset Transfer',
    'version': '5.4.1',
    'category' : 'Accounting',
    'license': 'Other proprietary',
    'depends': [
        'odoo_account_asset',
        'hr',
        'odoo_account_asset_extend_ce',
    ],
    'currency': 'EUR',
    'price': 99.0,
    'summary': """Account Asset Transfer Feature""",
    'description': """
Odoo Asset Transfer
Asset Transfer Report
Asset Transfer,
Asset Transfer Pivot Report
Asset Transfer Type
Transfer Type Configuration
Transfer for Asset
Asset Transfer Type
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
#    'live_test_url': 'https://youtu.be/gkU-pnHNUGc',
    #'live_test_url': 'https://youtu.be/izA9ppjflKk',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_asset_transfer_ce/617',#' https://youtu.be/O99qBDeo0NU',
    'data':[
            'security/ir.model.access.csv',
            'data/asset_accountability_transfer_sequance.xml',
            'report/asset_accountability_transfer_report.xml',
            'views/asset_accountability_transfer_view.xml',
            'views/asset_transfer_type_view.xml',
            'views/asset_accountability_transfer_report_view.xml',
            'views/account_asset_view.xml',
            'views/asset_menu_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
