# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "odoo product validation price ",
    "category": 'Sales',
    "summary": 'odoo product validation price greater than cost',
    "description": """

    odoo product validation price greater than cost
    """,
    "sequence": 1,
    "author": "me",
    "website": "https://www.me.in",
    "version": '16.0.0.2',
    "depends": ['product','sh_pos_all_in_one_retail','sale'],
    "data": [
        'data.xml',
        
    ],
   
    "installable": True,
    "application": False,
    "auto_install": False,
   
}
