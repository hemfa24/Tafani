# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quotation from CRM Opportunity Extended',
    'version': '7.2.4',
    'price': 25.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Sales',
    'summary': 'This module allow to add products on Opportunity and create quote with that.',
    'description': """ 
This module allow to add products on Opportunity and create quote with that.

sale_crm
crm
Opportunity  
quotation Opportunity
Opportunity lines
product lines on Opportunity
crm quote
crm quote lines
customer product lines
create quotation from crm
sales team quotation
sales team products
linked to the generated sales order
link sales order with Opportunity
Opportunity on sales order.
crm purchase order
crm purchse tendor
lead purchase
opportunity purchase order
opportunity quotation
opportunity rfq
opportunity request for quote
opportunity request for quotation
crm opportunity
opportunity purchase order line
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_opportunity_quotation/966',#'https://youtu.be/-MmpzBlpw_4',
    'images': ['static/description/img1.jpg'],
    'depends': ['crm', 'sale_crm', 'stock'],
    'data': [
            'security/ir.model.access.csv',
            'views/opportunity_quotation_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
