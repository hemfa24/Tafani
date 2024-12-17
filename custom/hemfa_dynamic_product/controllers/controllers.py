# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaDynamicProduct(http.Controller):
#     @http.route('/hemfa_dynamic_product/hemfa_dynamic_product', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_dynamic_product/hemfa_dynamic_product/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_dynamic_product.listing', {
#             'root': '/hemfa_dynamic_product/hemfa_dynamic_product',
#             'objects': http.request.env['hemfa_dynamic_product.hemfa_dynamic_product'].search([]),
#         })

#     @http.route('/hemfa_dynamic_product/hemfa_dynamic_product/objects/<model("hemfa_dynamic_product.hemfa_dynamic_product"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_dynamic_product.object', {
#             'object': obj
#         })
