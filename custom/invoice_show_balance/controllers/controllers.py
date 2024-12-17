# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceShowCustomerBalance(http.Controller):
#     @http.route('/invoice_show_customer_balance/invoice_show_customer_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_show_customer_balance/invoice_show_customer_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_show_customer_balance.listing', {
#             'root': '/invoice_show_customer_balance/invoice_show_customer_balance',
#             'objects': http.request.env['invoice_show_customer_balance.invoice_show_customer_balance'].search([]),
#         })

#     @http.route('/invoice_show_customer_balance/invoice_show_customer_balance/objects/<model("invoice_show_customer_balance.invoice_show_customer_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_show_customer_balance.object', {
#             'object': obj
#         })
