# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request

class SetBranch(http.Controller):

    @http.route('/set_brnach_rule', type='json', auth="public", methods=['POST'], website=True)
    def custom_branch(self, allowledbid, **post):
        branch_obj=request.env['res.branch'].sudo()
        branch_id = branch_obj.search([('id', 'in', allowledbid)])
        user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)])
        branch_id_set = branch_obj.search([('id', '=', allowledbid[0])])
        user_id.branch_id=branch_id_set
        user_id.res_branch_ids=branch_id

    @http.route('/set_brnach', type='json', auth="public", methods=['POST'], website=True)
    def custom_hours(self, BranchID, **post):
        user_id = request.env['res.users'].sudo().search([('id','=',request.env.user.id)])
        branch_ids = user_id.branch_ids.ids
        user_id.branch_id = BranchID[0]
        set_branch_ids = []
        if branch_ids and BranchID:
            for branch in BranchID:
                if branch in branch_ids:
                    set_branch_ids.append(branch)
            user_id.write({'res_branch_ids':[(6, 0, set_branch_ids)]})
        return
