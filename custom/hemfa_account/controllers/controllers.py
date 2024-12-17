# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaAccount(http.Controller):
#     @http.route('/hemfa_account/hemfa_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_account/hemfa_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_account.listing', {
#             'root': '/hemfa_account/hemfa_account',
#             'objects': http.request.env['hemfa_account.hemfa_account'].search([]),
#         })

#     @http.route('/hemfa_account/hemfa_account/objects/<model("hemfa_account.hemfa_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_account.object', {
#             'object': obj
#         })
