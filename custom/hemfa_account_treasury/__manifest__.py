# -*- coding: utf-8 -*-
{
    'name': "hemfa_account_treasury",

    'summary': """
        100_hemfa_account_treasury_R_D_16.0.0.2_2023.06.8
	treasury management  sending cash / treasury management receiving cash / bank transfer/fix Dashboard
""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Hemfa",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.7',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'base_accounting_kit', 'hemfa_account',],

    # always loaded
    'data': [
        'views/account_payment.xml',
        'views/account_treasury_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

