# -*- coding: utf-8 -*-
{
    'name': "Dynamic Barcode Labels Custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "E.Mudathir",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # pos_retail_custom
    'depends': ['dynamic_barcode_labels', 'product'],

    # always loaded
    'data': [
        # 'security/barcode_label_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizard/barcode_labels.xml',
        'views/templates.xml',
        'report/barcode_labels_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
