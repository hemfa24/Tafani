# -*- coding: utf-8 -*-
{
    'name': "custom_opening_balance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    "assets": {
        "point_of_sale.assets": [
            "custom_opening_balance/static/src/js/CashOpeningPopup.js",
        ],

    },
    # only loaded in demonstration mode
    'demo': [
    ],
}
