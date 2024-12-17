# -*- coding: utf-8 -*-
{
    'name': "Account Treasury Commission",

    'summary': """
        Account Treasury Commission
""",

    'description': """
        Account Treasury Commission
    """,

    'author': "Kalim",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '16.0.10.6',

    'depends': [
        'account',
        'base_accounting_kit',
        'hemfa_account',
        'hemfa_account_treasury',
        'pways_commission_mgmt',
        'account_analytic_payment',
        'sale',
    ],

    'data': [
        'views/commission_view.xml',
        'views/account_payment_view.xml',
    ],
}
