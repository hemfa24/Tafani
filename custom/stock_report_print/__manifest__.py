# -*- coding: utf-8 -*-
{
    'name': "Stock Report PDF",

    'summary': """
       print stock report, stock report pdf, print stock report pdf, product report pdf, product stock pdf, product stock with overall total purchased and total sold quantities""",

    'description': """
       print stock report, stock report pdf, print stock report pdf, product report pdf, product stock , product stock with overall total purchased and total sold quantities""",


    'author': "Kaizen Principles",
    'website': 'https://erp-software.odoo-saudi.com/discount/',


    'category': 'Stock',
    'version': '0.1',
    'license': 'OPL-1',
    'depends': ['base', 'stock', 'stock_account', 'sale', 'purchase'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],

    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,

}
