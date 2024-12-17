# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Sequence Number CRM Opportunity',
    'version': '4.1.3',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/unique_sequence_crm_opportunity/330',#'https://youtu.be/444LrP7fSns',
    'summary': """generates a unique sequence number of lead/opportunity when it will be created.""",
    'description': """
Unique Sequence Crm Opportunity
lead number
opportunity number
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'images': ['static/description/image.png'],
    'category' : 'Website/Website',
    'depends': [
               'website_crm_partner_assign',
               ],
    'data': [
            'data/ir_sequence_data.xml',
            'views/crm_lead_view.xml',
            'views/crm_opportunity_view.xml',
            'views/template_view.xml'
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
