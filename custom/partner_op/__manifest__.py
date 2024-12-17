# -*- coding: utf-8 -*-
{
    'name': "HEMFA Partner Openning Balance",

    'summary': """
         100_partner_op_R_D_16.0.0.1_2023.05.11 
         Add Opening balance for a partner to show OP For Invoice and Vendor Bill """,

    'description': """
        Add Openning balance for partner to show OP For Invoice and Vendor Bill and Move
    """,

    'author': "HEMFA - E.Mudathir",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '16.0.0.2',
 

    # any module necessary for this one to work correctly
    'depends': ['sale', 'purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'wizard/resPartnerOpBalanceWizardView.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    
}
