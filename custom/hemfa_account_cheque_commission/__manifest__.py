# -*- coding: utf-8 -*-
{
    'name': "Account Cheque Commission",

    'summary': """
        Account Cheque Commission
""",

    'description': """
        Account Cheque Commission
    """,

    'author': "Kalim",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '16.0.1.0',

    'depends': [
        'account',
        'base_accounting_kit',
        'hemfa_account',
        'hemfa_account_treasury',
        'pways_commission_mgmt',
        'account_analytic_payment',
        'sale',
        'hemfa_account_cheque',
    ],

    'data': [
        'views/commission_view.xml',
        'views/account_cheque_view.xml',
    ],
}
