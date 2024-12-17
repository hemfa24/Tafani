# -*- coding: utf-8 -*-
##########################################################################
# Author      : Nevioo Technologies (<https://nevioo.com/>)
# Copyright(c): 2020-Present Nevioo Technologies
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
{
    "name":  "Product Import",
    "summary":  "Import Product Template and its Variants using xls and csv file. If the products are available in system then it will be updated else will create a new one",
    "category":  "Import",
    "version":  "16.0.2.13",
    "sequence":  1,
    "price": "18.00",
    "currency": "USD",
    "license": 'OPL-1',
    "images": ['static/description/Banner.gif'],
    "author":  "Nevioo Technologies",
    "website":  "www.nevioo.com",
    "depends":  ['base', 'sale','stock','product'],
    #"depends":  [ 'sale_management'],
    'data': [
                'security/ir.model.access.csv',
                'wizard/ni_product_template_import_view.xml',
                'views/product_view.xml',
                'views/res_config_settings_views.xml',
                
            ],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
}
##########################################################################
