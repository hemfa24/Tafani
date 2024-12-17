# Copyright (C) Softhealer Technologies.

from . import models
from odoo import api, SUPERUSER_ID

def uninstall_hook(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})
    custom_fields = env['sh.custom.field.model'].sudo().search([])

    for field in custom_fields:
        try:
            if field:
                field.unlink()
        except Exception as e:

            print("\n\n\n\n %s field not found \n %s"%(field.name,e))

    custom_tabs = env['sh.custom.model.tab'].sudo().search([])

    for tab in custom_tabs:
        try:
            if tab:
                tab.unlink()
        except Exception as e:

            print("\n\n\n\n %s tab not found \n %s"%(tab,e))

