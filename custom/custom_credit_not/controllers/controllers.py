# -*- coding: utf-8 -*-
# from odoo import http


# class CustomCreditNot(http.Controller):
#     @http.route('/custom_credit_not/custom_credit_not', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_credit_not/custom_credit_not/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_credit_not.listing', {
#             'root': '/custom_credit_not/custom_credit_not',
#             'objects': http.request.env['custom_credit_not.custom_credit_not'].search([]),
#         })

#     @http.route('/custom_credit_not/custom_credit_not/objects/<model("custom_credit_not.custom_credit_not"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_credit_not.object', {
#             'object': obj
#         })
