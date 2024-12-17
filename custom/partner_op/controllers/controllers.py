# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerOp(http.Controller):
#     @http.route('/partner_op/partner_op/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_op/partner_op/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_op.listing', {
#             'root': '/partner_op/partner_op',
#             'objects': http.request.env['partner_op.partner_op'].search([]),
#         })

#     @http.route('/partner_op/partner_op/objects/<model("partner_op.partner_op"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_op.object', {
#             'object': obj
#         })
