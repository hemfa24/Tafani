# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'RFQ-Purchase Order From CRM Opportunity',
    'version': '7.3.9',
    'currency': 'EUR',
    'price': 25.0,
    'license': 'Other proprietary',
    'category': 'Sales/CRM',
    'summary': 'This module allow to create Purchase order/ RFQ from Opportunity.',
    'description': """ 
This module allow to create Purchase order/ RFQ from Opportunity.
crm purchase order
crm opportunity purchase
purchase order from crm
purchase order from opportunity
rfq opportunity
opportunity rfq
opportunity po
opportunity purchse
opportunity product
opportunity products
rfq produts
crm lead
crm purchse request
purchase request
team purchase
purchase team
sale_crm
crm
purchase module and crm module
Opportunity
Request for quotation Opportunity
Opportunity lines
product lines on Opportunity
crm quote
crm quote lines
customer product lines
create request for quotation from crm
sales team request for quotation
sales team products
linked to the generated purchase order
link purchase order with Opportunity
Opportunity on purchase order.
purchse order from Opportunity
create purchase order from Opportunity
rfq from Opportunity
create rfq from Opportunity
purchase order
rfq
crm extend
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['crm','purchase','stock'],
    'images': ['static/description/image.jpg'],
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_opportunity_purchase/965',#'https://youtu.be/sxzZG02Kc1k',
    'data': [
            'security/ir.model.access.csv',
            'views/opportunity_purchase_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
