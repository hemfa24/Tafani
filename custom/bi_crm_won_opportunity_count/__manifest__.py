# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name":"CRM Won Opportunity Count",
    "version":"16.0.0.1",
    "category":"Sales",
    "summary":"count crm won opportunity crm sales won opportunity crm won pipeline crm sale opportunity crm sales pipeline employee won opportunity crm won opportunity report crm project pipeline crm sales lead opportunity crm lead pipeline crm opportunity",
    "description":"""The CRM Won Opportunity Count Odoo app is a dynamic tool that provides comprehensive count of won opportunities of employee. With this app, businesses can easily access a detailed count of the opportunities that have been successfully won by specific employee. This count provides a clear overview of the deals that have been closed successfully.""",
    "license": "OPL-1",
    "author" : "BrowseInfo",
    "website": "https://www.browseinfo.com",
    "depends":["base",
               "crm",
               "hr",
	          ],
    "data":[
            "views/crm_menu_views.xml",
            "views/res_config_setting_view.xml",
            "views/hr_employee_view.xml",
	       ],
    "auto_install": False,
    "application": True,      
    "installable": True,
    "images":['static/description/CRM Won-Opportunity-Count-Banner.gif'],
    'live_test_url':'https://youtu.be/mNcmTIV55qs',
}
