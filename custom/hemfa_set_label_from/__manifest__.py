# -*- coding: utf-8 -*-
{
    'name': "hemfa set label from ref",

    'summary': """
      set_label_from_ref
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.hemfa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.4',

    # any module necessary for this one to work correctly
    'depends': ['account','hemfa_account_cheque'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'view.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
