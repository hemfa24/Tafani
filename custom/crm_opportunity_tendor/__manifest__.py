# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Agreements / Tendor / Requisition from CRM Opportunity',
    'version': '6.2.7',
    'depends': [
                'crm_opportunity_purchase',
                'purchase_requisition',
                'stock',
                ],
    'currency': 'EUR',
    'license': 'Other proprietary',    
        'price': 75.0,

    'category': 'Sales/CRM',
    'summary': 'This app allow you to create Purchase Agreements / Tendor / Requisition from CRM Opportunity form.',
    'description': """ 
This module allow to create Purchase Requisition / Tender Opportunity
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
Opportunity purchase tendor
Opportunity purchase agreement
Opportunity purchase Requisition
crm purchase tendor
crm purchase agreement
crm purchase Requisition
crm purchase order
pipeline purchase agreement
pipeline purchase Requisition
crm purchase order
crm opportunity purchase
purchase agreement
purchase order from crm
purchase order from opportunity
rfq opportunity
opportunity rfq
opportunity po
opportunity purchse
opportunity product
opportunity products
Purchase Agreements
Purchase Agreement
vendor Purchase Agreements
vendor Agreements
vendor Agreement
crm vendor Agreement
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
    'images': ['static/description/image.jpg'],
    'support': 'contact@probuse.com',
    # 'live_test_url': 'https://youtu.be/kM4zu69tPXc',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_opportunity_tendor/974',#'https://youtu.be/jTcMUw4fvnY',
    'data': [
             'views/purchase_opportunity_tender.xml',
             'views/crm_lead_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
