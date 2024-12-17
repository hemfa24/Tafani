# -*- coding: utf-8 -*-
{
    'name': "Merge Discount Barcode Scan",

    'summary': """
        Merge Discount Barcode Scan
""",

    'description': """
        Merge Discount Barcode Scan
        TO fix an issue to recompute price unit using onchange from sales order line
    """,

    'author': "Kalim",
    'website': "https://www.yourcompany.com",

    'category': 'Sales',
    'version': '16.0.0.1',

    'depends': [
        'account',
        'bi_sale_purchase_discount_with_tax',
        'sh_barcode_scanner',
    ],

    'data': [
    ],
}
