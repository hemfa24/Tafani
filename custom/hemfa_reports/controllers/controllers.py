# -*- coding: utf-8 -*-
# from odoo import http


# class HemfaReports(http.Controller):
#     @http.route('/hemfa_reports/hemfa_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hemfa_reports/hemfa_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hemfa_reports.listing', {
#             'root': '/hemfa_reports/hemfa_reports',
#             'objects': http.request.env['hemfa_reports.hemfa_reports'].search([]),
#         })

#     @http.route('/hemfa_reports/hemfa_reports/objects/<model("hemfa_reports.hemfa_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hemfa_reports.object', {
#             'object': obj
#         })
