# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
###############################################################################
{
    "name": "Salesperson own Products",
    "category": 'Generic Modules/Product Management',
    "version": '16.0.0.1',
    "sequence":1,
    "summary": """
          800_kits_specific_product_for_user_R_S_R16.0.0.1_17-5-2023 -  odoo Apps will help to Salesperson can see own product & create thair Sale Orders.
        """,
    "description": """
Odoo Apps will help to Salesperson can see own products & create thair Sale Orders.      
    """,
    'author' : 'Keypress IT Services',

    'website' : 'https://www.keypress.co.in',
    "depends": ['sale','product',],
    "data": [
        'security/ir.model.access.csv',
        'security/group.xml',        
        'views/product_template_view.xml',
        'wizard/kits_assigne_sales_person_to_product_wizard.xml',
    ],
    "images":['static/description/Banner.png'],  
    'live_test_url':'https://youtu.be/bVTHyTPRZFo',
    "installable": True,
    "application": True,
    "auto_install": False,
    'price':12.0,
    'currency':'USD', 

}
