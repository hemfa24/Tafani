# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentFromSalePurchase(http.Controller):
#     @http.route('/hemfa_payment_from_sale_purchase/hemfa_payment_from_sale_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_payment_from_sale_purchase/hemfa_payment_from_sale_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_payment_from_sale_purchase.listing', {
#             'root': '/hemfa_payment_from_sale_purchase/hemfa_payment_from_sale_purchase',
#             'objects': http.request.env['hemfa_payment_from_sale_purchase.hemfa_payment_from_sale_purchase'].search([]),
#         })

#     @http.route('/hemfa_payment_from_sale_purchase/hemfa_payment_from_sale_purchase/objects/<model("hemfa_payment_from_sale_purchase.hemfa_payment_from_sale_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_payment_from_sale_purchase.object', {
#             'object': obj
#         })
