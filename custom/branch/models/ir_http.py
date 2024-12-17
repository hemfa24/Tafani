# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.http import request
import json
from odoo.tools import file_open, image_process, ustr
import hashlib
import odoo


class Http(models.AbstractModel):
    _inherit = 'ir.http'


    def session_info(self):
        """ Add information about iap enrich to perform """
        # user = request.env.user
        user = self.env.user
        session_info = super(Http, self).session_info()

        if self.env.user.has_group('base.group_user'):
            # the following is only useful in the context of a webclient bootstrapping
            # but is still included in some other calls (e.g. '/web/session/authenticate')
            # to avoid access errors and unnecessary information, it is only included for users
            # with access to the backend ('internal'-type users)
            menus = self.env['ir.ui.menu'].load_menus(request.session.debug)
            ordered_menus = {str(k): v for k, v in menus.items()}
            menu_json_utf8 = json.dumps(ordered_menus, default=ustr, sort_keys=True).encode()
            session_info['cache_hashes'].update({
                "load_menus": hashlib.sha512(menu_json_utf8).hexdigest()[:64], # sha512/256
            })
            if user:
                session_info.update({
                    # current_company should be default_company
                    "user_companies": {
                        'current_company': user.company_id.id,
                        'allowed_companies': {
                            comp.id: {
                                'id': comp.id,
                                'name': comp.name,
                                'sequence': comp.sequence,
                            } for comp in user.company_ids
                        },
                    },
                    "user_branches": {
                        'current_branch': user.branch_id.id , 
                        'allowed_branches': {
                            comp.id: {
                                'id': comp.id,
                                'name': comp.name,
                                'company': comp.company_id.id,
                            } for comp in user.branch_ids
                        },
                    },
                    "show_effect": True,
                    "currencies": self.sudo().get_currencies(),
                    "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
                    "display_switch_branch_menu": user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
                    "allowed_branch_ids" : user.branch_id.ids,
                })
        return session_info
    