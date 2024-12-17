# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "POS Order Quick Process",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point of Sale",
    "license": "OPL-1",
    "summary": "500_sh_pos_quick_order_R_S_R16.0.2_18-5-2023 - pos order quick process",
    "description": """This module useful for make pos order process quick by shortcut keys. only you need to press "p" key and it will print receipt directly. Very useful where there are not multiple payment methods and cash amount fixed. On single keypress it printed receipt.""",
    "version": "16.0.2",
    "depends": ["base", "point_of_sale"],
    "application": True,
    "data": [
        'views/res_config_settings.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'sh_pos_quick_order/static/src/js/quick_order_btn.js',
            'sh_pos_quick_order/static/src/xml/quick_order_btn.xml',
        ],
        
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "price": 18,
    "currency": "EUR"
}
