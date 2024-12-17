# -*- coding: utf-8 -*
# TL Technology (thanhchatvn@gmail.com)
{
    "name": "POS Login Direct",
    "version": "16.0.0.2",
    "category": "Point of Sale",
    "live_test_url": "http://posodoo.com",
    "author": "TL Technology",
    "summary":
        """
        500_pos_login_direct_R_D_R16.0.0.2_2023.05.23
        POS Login Direct Allow POS User login direct to POS Screen bypass backend layout Allow POS User logout from pos by pass backend layout - Close Cash Popup+  Creat user
        """,
    "description":
        """
        POS Login Direct \n
        Allow POS User login direct to POS Screen by pass backend layout \n
        Allow POS User logout from pos by pass backend layout
        """,
    "sequence": 0,
    "depends": ["point_of_sale"],
    "demo": [],
    "data": [
        "views/res_users_views.xml"
    ],
    "qweb": [

    ],
    "price": "70",
    "website": "http://posodoo.com",
    "currency": "EUR",
    "installable": True,
    "auto_install": False,
    "application": True,
    "external_dependencies": {},
    "images": ["static/description/icon.png"],
    "support": "thanhchatvn@gmail.com",
    "license": "OPL-1",
    "post_init_hook": "_auto_clean_cache_when_installed",
    "assets": {
        "point_of_sale.assets": [
            "pos_login_direct/static/src/js/ClosePosPopup.js",
           "pos_login_direct/static/src/js/Chrome.js",
            "pos_login_direct/static/src/js/HeaderButton.js",
        ],
        "web.assets_backend": [

        ],
        "point_of_sale.pos_assets_backend": [

        ],
        "web.assets_qweb": [
           # "pos_login_direct/static/src/xml/*",
        ],
    },
}
