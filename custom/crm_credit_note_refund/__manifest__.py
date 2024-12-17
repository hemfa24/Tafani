# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Credit Note from CRM',
    'version': '4.2.3',
    'price': 39.0,
    'depends': [
        'crm',
        'account',
    ],
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Create Credit Note from CRM Pipeline Form""",
    'description': """
        Create Credit Note from CRM Pipeline Form
        CRM with Credit Note Odoo App
        CRM App with Credit Note in Account App Odoo
        Allow your sales manager to create a credit note from the CRM form by selecting an invoice related to that customer.
        Credit notes can be created using a selected invoice in the wizard.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/crm_credit_note_refund/366',#'https://youtu.be/9nMZsYhoezo',
    'category' : 'Sales/CRM',
    'data':[
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'wizard/add_invoice_credit_note_views.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
