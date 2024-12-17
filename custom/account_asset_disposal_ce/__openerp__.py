# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Asset Disposal',
    'version': '1.0',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'license': 'Other proprietary',
    'category': 'Accounting & Finance',
    'price': 120.0,
    'currency': 'EUR',
    'summary': 'Account Asset Disposal - Version 8.0',
    'website': 'https://www.probuse.com',
    'description': """
    Account Asset Disposal

This module enables the feature to dispose the asset. User can use two below methods to dispose any asset.
Sales Dispose
Asset Write-Off
This will allow user to dispose asset of company directly from Asset form. We have provide new tab under Asset form. 
You can see blog of our here on this: http://www.probuse.com/blog/erp-functional-27/post/asset-disposal-write-off-69 
**Note: This module only support Invoice sales of Asset not Cash sales.
""",
    'depends': ['account_asset'],
    'data': [
             'views/asset_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
