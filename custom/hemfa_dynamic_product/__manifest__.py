# -*- coding: utf-8 -*-
{
    'name': "hemfa dynamic product",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "16.0.2.18",


    # any module necessary for this one to work correctly 'bi_multiwarehouse_for_sales'
    'depends': ['product','sh_pos_all_in_one_retail', 'sale_management' ,'sh_barcode_scanner','bi_multi_uom_pricelist','inventory_adjustment_template','hemfa_warehouse_stock_request','bi_multiwarehouse_for_sales','bi_multiwarehouse_for_purchase','dynamic_barcode_labels','tis_price_checker_kiosk'],

    # always loaded
    'data': [
        
        #'security/barcode_label_security.xml',
        'security/ir.model.access.csv',
       # 'views/dynamic_product_barcode_line.xml',
        'views/product_dynamce.xml',
        'views/product_uom.xml',
        'wizard/barcode_labels.xml',
        'report/barcode_labels_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
