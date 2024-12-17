# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Update CRM Stage Pipeline',
    'version': '4.2.3',
    'category': 'Sales/CRM',
    'price': 15.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': [
        'crm'
    ],
    'summary': 'Mass Update CRM Lead / Pipeline Stage',
    'description': """
This app will allow your sales team user to update CRM pipelines / leads / opportunity from the list view in bulk for the same team. If the user
tries to select record(s) from different sales teams on the list then the system will raise a warning.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/mass_crm_pipeline_stage_update/312',#'https://youtu.be/peFDOAI4feY',
    'support': 'contact@probuse.com',
    'images': ['static/description/display.jpg'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mass_crm_pipeline_stage_wizard_views.xml',
        ],
    'installable': True,
    'application': False,
}
