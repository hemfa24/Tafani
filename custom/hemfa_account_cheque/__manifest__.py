# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hemfa Account Cheque Life Cycle Management Odoo',
    'version': '16.0.1.8',
    'category': 'Accounting',
    'summary': '100_hemfa_account_cheque_R_D_16.0.0.1_2023.05.11  sending Cheque Life Cycle.-receiving cheque life cycle ',
    'description' :"""Account Cheque management
    Account Cheque Life Cycle Management Odoo
    write cheque management Odoo,
    cheque management system Odoo
    write cheque system on Odoo
    incoming cheque management Odoo
    outgoing cheque management Odoo
    life cycle of cheque system Odoo
    life cycle of cheque management system Odoo
    complete cycle of cheque Odoo
    cheque incoming cycle odoo
    cheque outgoing cycle odoo
    deposit cheque Odoo, cashed cheque, reconcile cheque, cheque write management, cheque submit, cheque submission
    register cheque, cheque register management
    Bounce cheque, cheque Bounce management
    reconcile cheque with payment,
    reconcile cheque with advance payment
    Account reconcilation with cheque management
    return cheque management
    cheque return management
    journal entry from the cheque management system
    write cheque with reconcile system
    Accounting write cheque management system
    Transfer cheque managament odoo

    Account check management
    Account check Life Cycle Management Odoo
    write check management Odoo,
    check management system Odoo
    write check system on Odoo
    incoming check management Odoo
    outgoing check management Odoo
    life cycle of check system Odoo
    life cycle of check management system Odoo
    complete cycle of check Odoo
    check incoming cycle odoo
    check outgoing cycle odoo
    deposit check Odoo, cashed check, reconcile check, check write management, check submit, check submission
    register check, check register management
    Bounce check, check Bounce management
    Account reconcilation with check management
    return check management
    check return management
    journal entry from the check management system
    write check with reconcile system
    Accounting write check manahement system
    Transfer cheque management odoo
    PDC cheque management
    PDC check management 
    post dated cheque management
    post dated check managament

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base', 'account', 'hemfa_account_treasury', 'sale_management','hr'],
    'data': [
            'security/ir.model.access.csv',
            'security/account_cheque_security.xml',
            'report/account_cheque_report_view.xml',
            'report/account_cheque_report_template_view.xml',
            'views/account_cheque_view.xml',
            'views/account_payment.xml',
            'views/cheque_book_views.xml',
            'views/res_config_settings.xml',
            
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "price": 89,
    'license': 'LGPL-3',
    "currency": "EUR",
    'live_test_url':'https://youtu.be/RebVdk5DzIw',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
