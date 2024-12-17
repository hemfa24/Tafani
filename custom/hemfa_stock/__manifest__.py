# -*- coding: utf-8 -*-
{
    'name': "Hemfa stock",

    'summary': """
        costom stock""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Hemfa tech",
    'website': "http://www.hemfa.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'stock'],

    # always loaded
    'data': [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
        'views/hemfa_stock.xml',
        'views/templates.xml',
        'views/stock_warehouse.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
