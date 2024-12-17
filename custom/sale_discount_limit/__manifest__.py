# -*- coding: utf-8 -*-
{
    'name': "sale_discount_limit",

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
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['bi_sale_purchase_discount_with_tax'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
       'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
