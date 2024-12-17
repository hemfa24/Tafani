# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Purchase Multi Warehouse Odoo App",
    'version': '16.0.0.0',
    'category': 'Purchase',
    'summary': '300_bi_multiwarehouse_for_purchase_R_S_R16.0.0.0_15-5-2023 Purchase order Multi Warehouse for purchase order line',
    "description": """ This odoo app helps user to select multiple warehouse for purchase order and create incoming shipment order based on warehouse selected on purchase order line, User have to configure warehouse on product and on selecting product on purchase order line warehouse will selected, user can also change warehouse. """,
    'author': 'Browseinfo',
    'website': "https://www.browseinfo.in",
    "price": 25,
    "currency": 'EUR',
    'depends': ['base','stock','purchase'],
    'data': [
        'views/purchase_config_settings_views.xml',
        'views/product_template_inherit.xml',
        'views/product_product_inherit.xml',
        'views/purchase_order_views.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/hzPjov3kjzk',
    "images":['static/description/Banner.gif'],
    'license': 'OPL-1' ,
}
