# -*- coding: utf-8 -*-
# from odoo import http


# class Casound(http.Controller):
#     @http.route('/casound/casound', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/casound/casound/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('casound.listing', {
#             'root': '/casound/casound',
#             'objects': http.request.env['casound.casound'].search([]),
#         })

#     @http.route('/casound/casound/objects/<model("casound.casound"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('casound.object', {
#             'object': obj
#         })
