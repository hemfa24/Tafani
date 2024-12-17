# -*- coding: utf-8 -*-
# Part of CorTex IT Solutions Ltd.. See LICENSE file for full copyright and licensing details.

{
    'name': "Assets Management",
    'version': "16.0.0.0.1",
    'summary':  """Manage assets,
        Keeps track of depreciation's, and creates corresponding journal entries""",
    'category': 'Accounting/Accounting',
    'description': """Manage assets,
        Keeps track of depreciation's, and creates corresponding journal entries
Asset 
Asset Management
Odoo Asset Management
Assets
Odoo Asset
Odoo Assets
Odoo Assets Management
Assets Management
    """,
    'author': 'CorTex IT Solutions Ltd.',
    'website': 'https://cortexsolutions.net',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 50,
    'support': 'support@cortexsolutions.net',
    'depends': ['account'],
    'data': [
        'data/account_asset_data.xml',
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',
        'wizard/asset_sell_views.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
        'views/product_views.xml',
        'report/account_asset_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ctx_account_asset/static/src/scss/account_asset.scss',
            'ctx_account_asset/static/src/js/account_asset.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/main_screenshot.png'],
}