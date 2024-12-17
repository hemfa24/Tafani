# -*- coding: utf-8 -*-
{
    'name': "HEMFA Payment From Sale and Purchase",

    'summary': """
      100_hemfa_payment_from_sale_purchase_R_D_16.0.0.1_2023.05.11
      Cash Payment on  purchase order   payment on sales order
      """,

    'description': """
        HEMFA Payment From Sale and Purchase
    """,

    'author': "E.Mudathir",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','purchase','hemfa_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/account_payment_register_views.xml',
        'views/res_partner.xml',
        'views/purchase_views.xml',
        'views/sale_views.xml',
        'views/payment_views.xml',
        'views/templates.xml',
        
    ],

}
