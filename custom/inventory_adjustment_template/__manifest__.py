
# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Inventory Adjustments Template',
    'version': '16.0.0.2',
    'author': 'Geminate Consultancy Services',
    'description': """Inventory Adjustments Template  by selecting the product / by scan barcode/no    	barcode error'.""",
    'license': 'Other proprietary',
    'website': 'www.geminatecs.com',
    'category': 'stock',
    'summary': '400_inventory_adjustment_template_R_D_16.0.0.1_2023.06.01',
    'depends': [
            'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/load_template.xml',
        'wizard/select_products_wizard_view.xml',
        'views/stock_inventory_view.xml',
        

    ],
    'qweb': [
    ],
    'images':['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 39.99,
    'currency': 'EUR'    
}  


