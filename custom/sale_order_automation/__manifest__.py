# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Order Automation',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Sales',
    'maintainer': 'Craftsync Technologies',
    'summary': """200_sale_order_automation_R_S_R16.0.1.0_17-5-2023 - Enable auto sale workflow with sale order confirmation. Include operations like Auto Create Invoice, Auto Validate Invoice and Auto Transfer Delivery Order.""",
    'description': """

        You can directly create invoice and set done to delivery order by single click

    """,
    'website': 'https://www.craftsync.com/',
    'license': 'LGPL-3',
    'support':'info@craftsync.com',
    'depends' : ['sale_management','stock'],
    'data': [
        'views/stock_warehouse.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],

}
