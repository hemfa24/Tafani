# -*- coding: utf-8 -*-
# from odoo import http


# class AccountAnalyticPayment(http.Controller):
#     @http.route('/account_analytic_payment/account_analytic_payment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_analytic_payment/account_analytic_payment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_analytic_payment.listing', {
#             'root': '/account_analytic_payment/account_analytic_payment',
#             'objects': http.request.env['account_analytic_payment.account_analytic_payment'].search([]),
#         })

#     @http.route('/account_analytic_payment/account_analytic_payment/objects/<model("account_analytic_payment.account_analytic_payment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_analytic_payment.object', {
#             'object': obj
#         })
