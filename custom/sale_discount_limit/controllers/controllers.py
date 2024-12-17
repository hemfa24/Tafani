# -*- coding: utf-8 -*-
# from odoo import http


# class SaleDiscountLimit(http.Controller):
#     @http.route('/sale_discount_limit/sale_discount_limit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_discount_limit/sale_discount_limit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_discount_limit.listing', {
#             'root': '/sale_discount_limit/sale_discount_limit',
#             'objects': http.request.env['sale_discount_limit.sale_discount_limit'].search([]),
#         })

#     @http.route('/sale_discount_limit/sale_discount_limit/objects/<model("sale_discount_limit.sale_discount_limit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_discount_limit.object', {
#             'object': obj
#         })
