# -*- coding: utf-8 -*-
{
    'name': "Bi Hemfa 2.0 :",

    'summary': """
         @v16.0.0.1 - new module
        ~ Bi Hemfa Extend Module
        ------------------------
        @26 June 2024
        @v16.0.0.2 - new updated 
         - Added a new group for security
         - Add new validation: Users without group permission cannot
            create draft records for any type of Treasury account
    """,

    'description': """

    """,

    'author': "Hemfa",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '16.0.0.4',

    'depends': [
        'account',
        'hemfa_account_cheque'
    ],

    'data': [
        'security/security.xml',
        'views/res_company.xml',
    ],

}
