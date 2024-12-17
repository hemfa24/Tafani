# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Product Low Stock Notification",
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    "support": "support@softhealer.com",
    'version': '16.0.5',
    'category': "Warehouse",
    'summary': "400_sh_low_stock_notification_R_S_R16.0.5_18-5-2023 - Product Low Stock Alert,product low stock email, low stock product alert,product minimum stock alerts,warehouse low stock alerts, display low stock quantity, product stock alert,Minimum Stock Reminder,Print product Low Stock Report odoo",
    'description': """This module very useful to give email update to user regarding low stock of product. List of product appear in email with current stock evaluations. Easily define low stock level global for all products or individual product low stock level (qty). On basis of type of mode it will generate email if any product low stock.""",
    "depends": [
        'stock',
        'mail'
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'report/sh_low_stock_pdf_report_templates.xml',
        'report/sh_low_stock_xls_report_wizard_views.xml',
    ],
    'images': ['static/description/background.png', ],
    "live_test_url": "https://youtu.be/6FRkJn7hAtQ",
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "autoinstall": False,
    "price": 35,
    "currency": "EUR"
}
