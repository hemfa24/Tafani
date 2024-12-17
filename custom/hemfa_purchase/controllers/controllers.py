# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaPurchase(http.Controller):
#     @http.route('/hemfa_purchase/hemfa_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_purchase/hemfa_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_purchase.listing', {
#             'root': '/hemfa_purchase/hemfa_purchase',
#             'objects': http.request.env['hemfa_purchase.hemfa_purchase'].search([]),
#         })

#     @http.route('/hemfa_purchase/hemfa_purchase/objects/<model("hemfa_purchase.hemfa_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_purchase.object', {
#             'object': obj
#         })
