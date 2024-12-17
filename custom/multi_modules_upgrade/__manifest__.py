# -*- coding: utf-8 -*-
# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License OPL-1

{
    'name': "Multi Modules/Apps Upgrade",

    'summary': """
        This module enable you to filter local modules/apps needs an upgrade and allows you upgrade all of them
        with single click.
        """,
    'description': """
modules
apps
module
app
modules upgrade
modules update
module upgrade
module update
modules multi upgrade
modules multi update
multi upgrade
multi update
apps multi upgrade
apps multi update
update multi modules
upgrade multi modules
update multi apps
upgrade multi apps
multi modules upgrade
multi apps update
update modules
upgrade modules
update apps
upgrade apps
modules mass upgrade
mass modules upgrade
apps mass upgrade
mass apps upgrade
bulk upgrade
bulk update
modules bulk update
modules bulk upgrade
apps bulk update
apps bulk upgrade
    """,

    'author': 'CorTex IT Solutions Ltd.',
    'website': 'https://cortexsolutions.net',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 20,
    'support': 'support@cortexsolutions.net',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': [ 'base'],
    # always loaded
    'data': [
        'views/module_views.xml',
        'views/base_module_immediate_upgrade.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True
}
