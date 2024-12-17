# -*- coding: utf-8 -*-
{
    'name': "Stock Inventory Report",

    'summary': """
    An Inventory Report is a document created to track the quantity of goods that have been imported, exported, and remain in stock
       """,

    'description': """
     An Inventory Report is a document created to track the quantity of goods that have been imported, exported, and remain in stock. This report provides warehouse managers with the necessary information to manage and adjust the import and export of goods efficiently and meet customer demand. The information typically included in this report includes the quantity of inventory, the total value of inventory, the quantity of goods imported and the quantity of goods exported within a certain period of time.
    """,
    "price": "0",
    "currency": "EUR",
    'license': 'GPL-3',
    'author': "TTN SOFTWARE",
    'website': "TTNSOFTWARE.STORE",
    'category': 'App',
    'version': '15.1.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product', 'purchase', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'reports/casound_bao_cao_xuat_nhap_kho_report_template.xml',
        'reports/casound_bao_cao_gia_thanh_report_template.xml',
        'reports/report.xml',

        'wizard/casound_bao_cao_xuat_nhap_kho_wizard.xml',
        'wizard/casound_bao_cao_gia_thanh_wizard.xml',

        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/img/main_screenshot.gif']
}
