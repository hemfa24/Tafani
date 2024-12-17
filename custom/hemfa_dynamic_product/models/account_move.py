# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, api, fields,Command, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _add_product(self, barcode):
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""

        if self.env.company.sudo().sh_invoice_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_invoice_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_invoice_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_invoice_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_invoice_barcode_scanner_auto_close_popup) + "_MS&"

        if self and self.state != "draft":
            selections = self.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))

        # step 2 increaset product qty by 1 if product not in order line than create new order line.
        elif self:
            self.invoice_line_ids.with_context(check_move_validity=False).update({
                'sh_invoice_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
            })

            search_lines = False
            domain = []
            if self.env.company.sudo().sh_invoice_barcode_scanner_type == "barcode":
                search_lines = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.barcode == barcode)
                domain = [("barcode", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "int_ref":
                search_lines = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.default_code == barcode)
                domain = [("default_code", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "sh_qr_code":
                search_lines = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.sh_qr_code == barcode)
                domain = [("sh_qr_code", "=", barcode)]

            elif self.env.company.sudo().sh_invoice_barcode_scanner_type == "all":
                search_lines = self.invoice_line_ids.filtered(lambda ol: ol.product_id.barcode == barcode or
                                                              ol.product_id.default_code == barcode or
                                                              ol.product_id.sh_qr_code == barcode
                                                              )

                domain = ["|", "|",

                          ("default_code", "=", barcode),
                          ("barcode", "=", barcode),
                          ("sh_qr_code", "=", barcode)

                          ]

            if search_lines:
                # PICK LAST LINE IF MULTIPLE LINE FOUND
                search_lines = search_lines[len(search_lines) - 1]
                search_lines.quantity += 1
                search_lines.sh_invoice_barcode_scanner_is_last_scanned = is_last_scanned
                search_lines.sequence = sequence
            else:
                search_product = self.env["product.product"].search(
                    domain, limit=1)
                search_product_code = self.env["product.template.barcode"].sudo().search(
                    [('name', '=', barcode),
                     ('available_item', '=', True)
                     ], limit=1)
                if search_product:
                    self.invoice_line_ids = [Command.create({
                        'product_id': search_product.id,
                        'sh_invoice_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence': sequence,
                    })]
                elif search_product_code:
                    set_price = 0.0
                    obj_price = self.env['product.pricelist.item'].sudo().search([
                        ('product_id', '=', search_product_code.product_id.id),
                        ('uom_id', '=', search_product_code.unit.id),
                        ('pricelist_id', '=', self.pricelist_id.id)
                    ], limit=1)
                    if obj_price:
                        set_price = obj_price.fixed_price
                    else:
                        set_price = search_product_code.price
                    search_lines_code = self.invoice_line_ids.filtered(
                    lambda ol: ol.product_id.id == search_product_code.product_id.id and ol.price_unit == set_price)
                    if search_lines_code:
                        search_lines_code.sudo().write({"quantity": search_lines_code.quantity + 1
                                                        ,
                        "sh_invoice_barcode_scanner_is_last_scanned": is_last_scanned,
                        "sequence" : sequence,})

                    else:

                        vals = {
                            'product_id': search_product_code.product_id.id,
            
                        
                            'price_unit': set_price,
                            'sh_invoice_barcode_scanner_is_last_scanned': is_last_scanned,
                            'sequence': sequence,
                        }
                        # if search_product_code.unit:
                        #     vals.update({
                        #         "product_uom": search_product_code.unit.id,
                        #     })
                        # new_order_line = self.order_line.new(vals)
                        # self.order_line += new_order_line
                        self.invoice_line_ids = [Command.create(vals)]

                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
