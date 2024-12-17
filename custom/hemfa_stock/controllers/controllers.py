# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaStock(http.Controller):
#     @http.route('/hemfa_stock/hemfa_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_stock/hemfa_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_stock.listing', {
#             'root': '/hemfa_stock/hemfa_stock',
#             'objects': http.request.env['hemfa_stock.hemfa_stock'].search([]),
#         })

#     @http.route('/hemfa_stock/hemfa_stock/objects/<model("hemfa_stock.hemfa_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_stock.object', {
#             'object': obj
#         })
