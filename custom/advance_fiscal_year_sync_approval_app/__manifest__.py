# -*- coding: utf-8 -*-
{
    "name" : "Account Fiscal Year with Approval - Advance Fiscal Year App",
    "author": "Edge Technologies",
    "version" : "16.0.1.0",
    'live_test_url':'https://youtu.be/lMMF2GNXdqk',
    "images":['static/description/main_screenshot.png'],
    'summary': "100_advance_fiscal_year_sync_approval_app_R_S_R16.0.1.0_15-5-2023",
    "description": """
                App for creating opening journal entry for new fiscal year

                """,
    "license" : "OPL-1",
    "depends" : ['account','fiscal_year_sync_app'],
    "data": [
        'security/ir.model.access.csv',
        'security/fiscal_year_security.xml',
        'wizard/account_period_re_open_view.xml',
        'wizard/account_fiscalyear_re_open_view.xml',
        'views/account_fiscalperiod_view.xml',
        'views/account_fiscalyear_view.xml',
    ],
    "auto_install": False,
    "price": 48,
    "currency": 'EUR',
    "installable": True,
    "category" : "Accounting",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
