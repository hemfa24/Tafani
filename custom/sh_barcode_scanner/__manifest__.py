# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "All In One Barcode Scanner-Basic | Sale Order Barcode Scanner | Purchase Order Barcode Scanner | Invoice Barcode Scanner | Inventory Barcode Scanner | Bill Of Material Barcode Scanner | Scrap Barcode Scanner | Warehouse Barcode Scanner",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.2.9",

    "category": "Extra Tools",

    "summary": "Barcode Scanner Package,Sales Barcode Scanner,Purchase Barcode Scanner Module,Account Barcode Scanner,Stock Barcode Scanner,BOM Barcode Scanner,Request For Quotation Barcode Scanner,Bill Barcode Scanner,PO Barcode Scanner,RFQ Barcode Scanner Odoo",

    "description": """Do your time-wasting in sales, purchases, invoices, inventory, bill of material, scrap operations by manual product selection? So here are the solutions these modules useful do quick operations of sales, purchases, invoicing and inventory, bill of material, scrap using barcode scanner. You no need to select the product and do one by one. scan it and you do! So be very quick in all operations of odoo and cheers!

 All In One Barcode Scanner - Sales, Purchase, Invoice, Inventory, BOM, Scrap Odoo.
Operations Of Sales, Purchase Using Barcode, Invoice Using Barcode, Inventory Using Barcode, Bill Of Material Using Barcode, Scrap Using Barcode Module, Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner, Single Product Multi Barcode Odoo.
 
 Barcode Scanner App,Package All in one barcode scanner,  Operations Of Sales, Purchase In Barcode Module, Invoice In Barcode, Inventory In Barcode, Bom In Barcode, Scrap Using Barcode, Single Product Multi Barcode, Sales Barcode Scanner,Purchase Barcode Scanner, Invoice Barcode Scanner, Inventory Barcode Scanner,Bom Barcode Scanner, Single Product Multi Barcode Odoo.


Add products by barcode    
Add products using barcode    

sales mobile barcode scanner
so barcode scanner
so mobile barcode scanner
sale mobile barcode scanner

po mobile barcode scanner
purchase order mobile barcode scanner
purchase order barcode scanner
po barcode scanner
    
inventory mobile barcode scanner    
stock mobile barcode scanner
inventory barcode scanner
stock barcode scanner

inventory adjustment mobile barcode scanner
stock adjustment mobile barcode scanner
inventory adjustment barcode scanner
stock adjustment barcode scanner

invoice barcode scanner
bill barcode scanner
credit note barcode scanner
debit note barcode scanner
invoice barcode mobile scanner
bill barcode mobile scanner
credit note barcode mobile scanner
debit note barcode mobile scanner

     """,

    "depends": [
                "purchase",
                "sale_management",
                "barcodes",
                "account",
                "stock",
                "mrp",
                "sh_product_qrcode_generator",
    ],

    "data": [
        "security/ir.model.access.csv",
        # Sale
        "views/sale/sale_order_views.xml",
        "views/sale/res_config_settings_views.xml",

        # Purchase
        "views/purchase/purchase_order_views.xml",
        "views/purchase/res_config_settings_views.xml",

        # Stock Picking
        "views/stock_picking/stock_picking_views.xml",
        "views/stock_picking/res_config_settings_views.xml",

        # Stock Move
        "views/stock_move/stock_move_views.xml",

        # Stock Inventory
        "views/stock_inventory/res_config_settings_views.xml",

        # Stock Scrap
        "views/stock_scrap/stock_scrap_views.xml",
        "views/stock_scrap/res_config_settings_views.xml",

        # Invoice
        "views/account/account_move_views.xml",
        "views/account/res_config_settings_views.xml",

        # MRP BOM
        "views/mrp_bom/mrp_bom_views.xml",
        "views/mrp_bom/res_config_settings_views.xml",

        # Global Search Document
        "views/global_doc_search/res_config_settings_views.xml",

        # Product
        "views/product/product_template_views.xml",
        # Assets
        "views/stock_inventory/stock_adjustment_views.xml",

    ],
    "assets": {
        "web.assets_backend": [
            "sh_barcode_scanner/static/src/scss/sh_barcode_scanner.scss",
            "sh_barcode_scanner/static/src/js/warning_dialog.js",
            "sh_barcode_scanner/static/src/js/dialog.js",
            "sh_barcode_scanner/static/src/js/global_doc_search/global_doc_search.js",
            'sh_barcode_scanner/static/src/xml/global_doc_search/global_doc_search.xml',
            "sh_barcode_scanner/static/src/js/sh_inventory_adjustment_barcode_scanner.js",
            'sh_barcode_scanner/static/src/xml/sh_inventory_adjustment_barcode_scanner.xml',
        ],


    },

    "images": ["static/description/background.png", ],
    "installable": True,
    "application": True,
    "autoinstall": False,
    "price": 35,
    "currency": "EUR",
    "license": "OPL-1",
}
