# -*- coding: utf-8 -*-
{
    "name": "pos_custom_hemfa",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "point_of_sale", "product", "sale", "stock", "sh_pos_all_in_one_retail"],
    # always loaded
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        "wizard/close_session.xml",
        "views/views.xml",

        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_custom_hemfa/static/src/js/close_session.js",
            "pos_custom_hemfa/static/src/js/CustomClosePosPopup.js",
            "pos_custom_hemfa/static/src/js/CashOpeningPopup.js",
            # "pos_custom_hemfa/static/src/js/load_custom.js",
            "pos_custom_hemfa/static/src/xml/CustomClosePosPopup.xml",
        ],

    },
}
