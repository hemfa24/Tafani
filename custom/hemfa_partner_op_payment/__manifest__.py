# -*- coding: utf-8 -*-
{
    'name': "HEMFA Partner OP Payment",

    'summary': """
        100_hemfa_partner_op_payment_R_D_16.0.0.1_2023.05.11
        opening balance in treasury management """,

    'description': """
        Link and Reconcile Payment Opening balance with Moves 
    """,

    'author': "E.MUDATHIR",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['partner_op','hemfa_account_cheque'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_partial_payment.xml',
        'views/account_payment_view.xml',
        'views/account_cheque_view.xml',
        
        'views/templates.xml',
    ],
   
}
