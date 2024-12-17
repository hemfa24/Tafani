# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

{
    'name': 'Price Checker',
    'version': '13.0.0.2',
    'sequence': 1,
    'category': 'Warehouse',
    'summary': 'Price Checker Kiosk Mode',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'price': 85,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'description': """
    Price Checker Kiosk Mode
        """,
    'depends': ['product'],  # pos_retail
    'data': [
        'security/security.xml',
        'views/price_checker_kiosk_view.xml',
        # 'views/web_asset_backend_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "tis_price_checker_kiosk/static/src/js/price_checker_kiosk.js",
            "tis_price_checker_kiosk/static/src/xml/price_checker.xml",
            "tis_price_checker_kiosk/static/src/scss/price_checker.scss"
        ]},
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=fnSzjRjYyFw&feature=youtu.be'
}
