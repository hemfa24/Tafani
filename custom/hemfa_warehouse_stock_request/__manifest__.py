# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'HEMFA Inventory Warehouse Stock Request',
    'version' : '1.2.3',
    'price' : 29.0,
    'currency': 'EUR',
    'category': 'Inventory/Inventory',
    'license': 'Other proprietary',
    'live_test_url': 'http://probuseappdemo.com/probuse_apps/warehouse_stock_request/56',#'https://youtu.be/qZ5sm7dgvEg',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : '400_hemfa_warehouse_stock_request_R_D_16.0.0.1_2023.05.25 R Warehouse stock request py employee / from purchase / by notification / by access user',
    'description': """
This app allows your inventory stock user to create warehouse stock requests in inventory for internal transfer purposes of stock.
    - Allow your inventory users to create a warehouse stock request by filling a form given in below screenshots and submit a request to the inventory manager.
    - Allow your inventory manager to create an internal stock picking using the ‘Create Picking’ button.
    - Allow your inventory manager to finish a warehouse stock request manually.
    - For more details please check below screenshots and watch the video.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'stock','hr','purchase_requisition'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'report/warehouse_stock_request_report.xml',
        'data/mail_template.xml',
        'views/warehouse_stock_request_view.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        'views/menu.xml',
        'views/purchase_order.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
