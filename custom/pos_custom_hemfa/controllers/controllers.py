# -*- coding: utf-8 -*-
# from odoo import http


# class PosCustomHemfa(http.Controller):
#     @http.route('/pos_custom_hemfa/pos_custom_hemfa', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_custom_hemfa/pos_custom_hemfa/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_custom_hemfa.listing', {
#             'root': '/pos_custom_hemfa/pos_custom_hemfa',
#             'objects': http.request.env['pos_custom_hemfa.pos_custom_hemfa'].search([]),
#         })

#     @http.route('/pos_custom_hemfa/pos_custom_hemfa/objects/<model("pos_custom_hemfa.pos_custom_hemfa"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_custom_hemfa.object', {
#             'object': obj
#         })
