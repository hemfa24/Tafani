# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.scrap']

    def on_barcode_scanned(self, barcode):
        warm_sound_code = ""
        if self.env.company.sudo().sh_scrap_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_scrap_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_scrap_barcode_scanner_auto_close_popup) + "_MS&"

        # step 1: state validation.
        if self and self.state != 'draft':
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            warning_mess = {
                'title': _('Error!'),
                'message': (warm_sound_code + 'You can not scan item in %s state.') % (value)
            }
            return {'warning': warning_mess}

        elif self.product_id:

            if self.env.company.sudo().sh_scrap_barcode_scanner_type == 'barcode':
                if self.product_id.barcode == barcode:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message": (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'int_ref':
                if self.product_id.default_code == barcode:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message": (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'sh_qr_code':
                if self.product_id.sh_qr_code == barcode:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message": (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'all':
                if self.product_id.barcode == barcode or self.product_id.default_code == barcode or self.product_id.sh_qr_code == barcode:
                    self.scrap_qty += 1
                else:
                    warning_mess = {
                        "title": _("Error!"),
                        "message": (warm_sound_code + "You can not change product after scan started. If you want to scan new product than pls create new scrap.")
                    }
                    return {"warning": warning_mess}
        else:
            domain = []

            if self.env.company.sudo().sh_scrap_barcode_scanner_type == 'barcode':
                domain = [("barcode", "=", barcode)]

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'int_ref':
                domain = [("default_code", "=", barcode)]

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'sh_qr_code':
                domain = [("sh_qr_code", "=", barcode)]

            elif self.env.company.sudo().sh_scrap_barcode_scanner_type == 'all':
                domain = ["|", "|",
                          ("default_code", "=", barcode),
                          ("barcode", "=", barcode),
                          ("sh_qr_code", "=", barcode)
                          ]
            # ---------------------------------------------------
            # We set below domain if scrap wizard form view opened from
            # delivery order scrap button rather than menu item.
            # because you only scraped products that are existed in delivery/picking lines.
            # ---------------------------------------------------
            if self._context.get('product_ids', False):
                domain_product_ids = [
                    ("id", "in", self._context.get('product_ids'))]
                domain = expression.AND(
                    [domain, domain_product_ids])

            search_product = self.env["product.product"].search(
                domain, limit=1)
            if search_product:
                self.product_id = search_product.id

                # self.product_uom_id = search_product.uom_id.id

            else:
                warning_mess = {
                    "title": _("Error!"),
                    "message": (warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!" % (barcode))
                }
                return {"warning": warning_mess}
