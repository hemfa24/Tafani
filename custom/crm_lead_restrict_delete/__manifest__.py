# Copyright 2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Restrict CRM Lead Opportunities Delete",
    "summary": """
        This module helps to restrict the delete option for CRM Leads and Opportunities""",
    "description": """ This tiny app eliminates the option to delete a CRM Leads and Opportunities. """,
    "version": "16.0.1.0.0",
    "category": "crm",
    "website": "https://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "application": False,
    "depends": [
        "crm",
    ],
    "images": ["images/main_screenshot.jpg"],
    "data": [
        "security/security.xml",
        "views/crm_view.xml",
    ],
}
