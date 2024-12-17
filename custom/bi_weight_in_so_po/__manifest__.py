# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'All in One Weight Details in Sales, Purchase, Delivery',
    'version': '16.0.0.1',
    'category': 'Sales',
    'summary': '200_bi_bi_weight_in_so_po_R_S_R16.0.0.0_15-5-2023-All in One Total Weight on Sale Order/Purchase/inventory',
    'description' :"""

      All in One Weight in odoo,
      Product Weight in odoo,
      Calculate Product Weight into Sale Order in odoo,
      Calculate Product Weight into Purchase Order in odoo,
      Calculate Product Weight into Delivery Order in odoo,
      Calculate Product Weight into Customer Invoice in odoo,
      Calculate Product Weight into Vendor Bill in odoo,
      Total product Weight in odoo,

    """,
    'author': 'BrowseInfo',
    "price": 15,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['sale_management','purchase','stock','account'],
    'data': [

        'views/sale_weight_views.xml',
        'views/purchase_weight_views.xml',
        'views/stock_weight_views.xml',
        'views/account_weight_views.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/XN9JyZqUST0',
    "images":['static/description/Banner.gif'],
    'license': 'OPL-1',
}
