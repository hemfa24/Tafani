# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sh_sale_barcode_scanner_is_last_scanned = fields.Boolean(
        string="Last Scanned?")

    #New Added Code
    #Whene Select Manully product on order line
    @api.onchange('product_id', 'product_tmpl_id', 'product_uom_qty')
    def on_product_id_barcode(self):
        for rec in self:
            pricelist_id = rec.order_id.pricelist_id if rec.order_id else False
            if not pricelist_id:
                pricelist_id = self.env['product.pricelist'].search(
                    [], limit=1
                )
            rec.product_uom = rec.product_id.uom_id.id if\
                  rec.product_id.uom_id else False
            obj_price_stand = self.env['product.pricelist.item'].sudo().search(
                [
                        ('product_id', '=', rec.product_id.id),
                        ('uom_id', '=', rec.product_id.uom_id.id),
                        ('pricelist_id', '=', pricelist_id.id)
                ], limit=1
            )
            if obj_price_stand:
                rec.price_unit = obj_price_stand.fixed_price
            else:
                rec.price_unit = rec.product_id.list_price
    """
        5-Mar-2024
        Issue : Barcode scan
        1. Barcode scan @fields sale order view after customer screen
        2. successfully run
        3. now edit and change qty of sacn product then see unir price is change
        4. when you can agian change qty - 
            working but when you change re agian 
            is not work perfect like is oddn and even work

        @anaghanhiren
    """
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for line in self:
            pricelist_id = line.order_id.pricelist_id if\
                line.order_id else False
            PricelistObj = self.env['product.pricelist.item'].sudo()
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                obj_price_stand = PricelistObj.search([
                        ('product_id', '=', line.product_id.id),
                        ('uom_id', '=', line.product_id.uom_id.id),
                        ('pricelist_id', '=', pricelist_id.id)
                    ], limit=1)
                if obj_price_stand:
                    price = obj_price_stand.fixed_price
                price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )
                line.price_unit = price_unit


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    _barcode_scanned = fields.Char(
        "Barcode Scanned", help="Value of the last barcode scanned.", store=False)

    @api.onchange('_barcode_scanned')
    def _on_barcode_scanned(self):
        barcode = self._barcode_scanned
        if barcode:
            self._barcode_scanned = ""
            return self.on_barcode_scanned(barcode)

    def _add_product(self, barcode):
        is_last_scanned = False
        sequence = 0
        warm_sound_code = ""
        print ("\n\n\ = = = =  BARCODE SCANNER --- -- ", barcode)
        if self.env.company.sudo().sh_sale_barcode_scanner_last_scanned_color:
            is_last_scanned = True

        if self.env.company.sudo().sh_sale_barcode_scanner_move_to_top:
            sequence = -1

        if self.env.company.sudo().sh_sale_barcode_scanner_warn_sound:
            warm_sound_code = "SH_BARCODE_SCANNER_"

        if self.env.company.sudo().sh_sale_barcode_scanner_auto_close_popup:
            warm_sound_code += "AUTO_CLOSE_AFTER_" + \
                str(self.env.company.sudo(
                ).sh_sale_barcode_scanner_auto_close_popup) + "_MS&"

        # step 1 make sure order in proper state.
        if self and self.state in ["cancel", "done"]:
            selections = self.fields_get()["state"]["selection"]
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            raise UserError(
                _(warm_sound_code + "You can not scan item in %s state.") % (value))

        # step 2 increaset product qty by 1 if product not in order line than create new order line.
        elif self:

            self.order_line.update({
                'sh_sale_barcode_scanner_is_last_scanned': False,
                'sequence': 0,
            })

            search_lines = False
            domain = []
            if self.env.company.sudo().sh_sale_barcode_scanner_type == "barcode":
                search_lines = self.order_line.filtered(
                    lambda ol: ol.product_id.barcode == barcode)
                domain = [("barcode", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "int_ref":
                search_lines = self.order_line.filtered(
                    lambda ol: ol.product_id.default_code == barcode)
                domain = [("default_code", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "sh_qr_code":
                search_lines = self.order_line.filtered(
                    lambda ol: ol.product_id.sh_qr_code == barcode)
                domain = [("sh_qr_code", "=", barcode)]

            elif self.env.company.sudo().sh_sale_barcode_scanner_type == "all":
                search_lines = self.order_line.filtered(lambda ol: ol.product_id.barcode == barcode or
                                                        ol.product_id.default_code == barcode or
                                                        ol.product_id.sh_qr_code == barcode
                                                        )
                domain = ["|", "|",

                          ("default_code", "=", barcode),
                          ("barcode", "=", barcode),
                          ("sh_qr_code", "=", barcode)

                          ]
            if search_lines:
                for line in search_lines:
                    price = line.with_company(line.company_id)._get_display_price()
                    line.product_uom_qty += 1
                    line.sh_sale_barcode_scanner_is_last_scanned = is_last_scanned
                    line.sequence = sequence
                    line.price_unit = sequence
                    break
            else:
                search_product = self.env["product.product"].search(
                    domain, limit=1)
                print("...................127")
                if search_product:
                    vals = {
                        'product_id': search_product.id,
                        'name': search_product.name,
                        'product_uom': search_product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': search_product.lst_price,
                        'sh_sale_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence': sequence,
                    }
                    if search_product.uom_id:
                        vals.update({
                            "product_uom": search_product.uom_id.id,
                        })
                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

    def on_barcode_scanned(self, barcode):
        self._add_product(barcode)
