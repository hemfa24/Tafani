# -*- coding: utf-8 -*-
from odoo import http

# class PartialPayment(http.Controller):
#     @http.route('/partial_payment/partial_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partial_payment/partial_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partial_payment.listing', {
#             'root': '/partial_payment/partial_payment',
#             'objects': http.request.env['partial_payment.partial_payment'].search([]),
#         })

#     @http.route('/partial_payment/partial_payment/objects/<model("partial_payment.partial_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partial_payment.object', {
#             'object': obj
#         })