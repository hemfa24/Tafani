# -*- coding: utf-8 -*-
# from odoo import http


# class DynamicBarcodeLabelsCustom(http.Controller):
#     @http.route('/dynamic_barcode_labels_custom/dynamic_barcode_labels_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dynamic_barcode_labels_custom/dynamic_barcode_labels_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dynamic_barcode_labels_custom.listing', {
#             'root': '/dynamic_barcode_labels_custom/dynamic_barcode_labels_custom',
#             'objects': http.request.env['dynamic_barcode_labels_custom.dynamic_barcode_labels_custom'].search([]),
#         })

#     @http.route('/dynamic_barcode_labels_custom/dynamic_barcode_labels_custom/objects/<model("dynamic_barcode_labels_custom.dynamic_barcode_labels_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dynamic_barcode_labels_custom.object', {
#             'object': obj
#         })
