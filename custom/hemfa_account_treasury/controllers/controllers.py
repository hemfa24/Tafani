# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaAccountThearsury(http.Controller):
#     @http.route('/hemfa_account_thearsury/hemfa_account_thearsury', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_account_thearsury/hemfa_account_thearsury/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_account_thearsury.listing', {
#             'root': '/hemfa_account_thearsury/hemfa_account_thearsury',
#             'objects': http.request.env['hemfa_account_thearsury.hemfa_account_thearsury'].search([]),
#         })

#     @http.route('/hemfa_account_thearsury/hemfa_account_thearsury/objects/<model("hemfa_account_thearsury.hemfa_account_thearsury"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_account_thearsury.object', {
#             'object': obj
#         })
