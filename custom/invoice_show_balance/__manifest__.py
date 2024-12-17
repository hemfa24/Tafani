# -*- coding: utf-8 -*-
{
    'name': "Invoice Show Customer Balance",

    'summary': """
    	100_invoice_show_balance_R_D_R19.0.1.0.0_24-5-2023
        Show Customer Invoice Balance""",

    'description': """
        Show Customer Invoice Balance
    """,

    'author': "E.Mudathir",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoice',
    'version': '16.0.1.0.0',

    # any module necessary for this one to work correctly invoice_show_payment
    'depends': ['sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/sale.xml',
        'views/invoice.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
