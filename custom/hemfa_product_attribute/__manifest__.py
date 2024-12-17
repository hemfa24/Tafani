# -*- coding: utf-8 -*-
{
    'name': "hemfa product attribute",

    'summary': """
        200_hemfa_product_attribute_R_D_R16.0.1.6_6-25-2023 - Attribute values all in one +bill date+fix+adjustment line
        
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "hemfa",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    "version": "16.0.1.7",


    # any module necessary for this one to work correctly 'bi_multiwarehouse_for_sales'
    'depends': ['product','stock','hemfa_warehouse_stock_request','sale_management','ni_product_import' ,'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_attribute.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
