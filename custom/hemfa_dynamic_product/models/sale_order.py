# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, api, fields, _
from odoo.exceptions import UserError





class SaleOrderDynamic(models.Model):
    _inherit = "sale.order"
    #_inherit = ['sale.order', 'barcodes.barcode_events_mixin']


    # _barcode_scanned = fields.Char(
    #     "Barcode Scanned", help="Value of the last barcode scanned.", store=False)

    # @api.onchange('_barcode_scanned')
    # def _on_barcode_scanned(self):
    #     barcode = self._barcode_scanned
    #     if barcode:
    #         self._barcode_scanned = ""
    #         return self.on_barcode_scanned(barcode)

    def _add_product(self, barcode):
        is_last_scanned = False
       # self.is_multiwarehouse=True
        sequence = 0
        warm_sound_code = ""
        print ("Call - - --  THIS ALALLALALl")

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

            # self.order_line.update({
            #     'sh_sale_barcode_scanner_is_last_scanned': False,
            #     'sequence': 0,
            # })

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
                    """
                    HERI CODE
                    15 Dec 2023

                    Note : It seems there is a bug when scanning the product
                        for the second time; the system is unable to retrieve
                        the product's unit price, and it automatically
                        sets it to a default value of 0. - FIXED
                    """
                    price_unit = line.price_unit
                    price = line.with_company(line.company_id)._get_display_price()
                    line.product_uom_qty += 1
                    line.sh_sale_barcode_scanner_is_last_scanned = is_last_scanned
                    line.sequence = sequence
                    obj_price_stand = self.env['product.pricelist.item'].sudo().search([
                        ('product_id', '=', line.product_id.id),
                        ('uom_id', '=', line.product_uom.id),
                        ('pricelist_id', '=', self.pricelist_id.id)
                    ], limit=1)
                    if obj_price_stand:
                        line.price_unit = obj_price_stand.fixed_price
                    else:
                        line.price_unit = price_unit
                    #break
            else:
                print("\n\n 120 SALE ORDER ")
                search_product = self.env["product.product"].search(
                    domain, limit=1)
                search_product_code = self.env["product.template.barcode"].sudo().search(
                    [('name', '=', barcode),
                     ('available_item', '=', True)
                     ], limit=1)
                print("search_product_code", search_product_code)
                print("search_product", search_product)
                if search_product:
                    set_price_stand = 0.0
                    obj_price_stand = self.env['product.pricelist.item'].sudo().search([
                        ('product_id', '=', search_product.id),
                        ('uom_id', '=', search_product.uom_id.id),
                        ('pricelist_id', '=', self.pricelist_id.id)
                    ], limit=1)
                    if obj_price_stand:
                        set_price_stand = obj_price_stand.fixed_price
                    else:
                        set_price_stand = search_product.lst_price
                    print ("set_price_stand", set_price_stand)
                    vals = {
                        'product_id': search_product.id,
                        'name': search_product.name,
                        'product_uom': search_product.uom_id.id,
                        'product_uom_qty': 1,
                        'is_warehouse': True,
                        'warehouses_id':search_product.sale_warehouse_id.id,
                        'price_unit': set_price_stand,
                        'sh_sale_barcode_scanner_is_last_scanned': is_last_scanned,
                        'sequence': sequence,
                    }
                    if search_product.uom_id:
                        vals.update({
                            "product_uom": search_product.uom_id.id,
                        })
                    new_order_line = self.order_line.new(vals)
                    self.order_line += new_order_line
                elif search_product_code:
                    """
                        Dynamic Barcode product fields search
                        param: this method can b use
                        search: product.pricelist.item
                    """
                    set_price = 0.0
                    if search_product_code:
                        obj_price = self.env['product.pricelist.item'].sudo().search([
                            ('product_id', '=', search_product_code.product_id.id),
                            ('uom_id', '=', search_product_code.unit.id),
                            ('pricelist_id', '=', self.pricelist_id.id)
                        ], limit=1)
                        if obj_price:
                            set_price = obj_price.fixed_price
                        else:
                            set_price = search_product_code.price
                    else:
                        set_price = search_product_code.price
                    search_lines_code = self.order_line.filtered(
                    lambda ol: ol.product_id.id == search_product_code.product_id.id and ol.product_uom.id ==search_product_code.unit.id and ol.price_unit == set_price)
                    if search_lines_code:
                        search_lines_code.sudo().write({
                            "product_uom_qty": search_lines_code.product_uom_qty + 1,
                            "sh_sale_barcode_scanner_is_last_scanned": is_last_scanned,
                            "sequence": sequence,
                            "price_unit": set_price
                        })

                    else:
                        vals = {
                            'product_id': search_product_code.product_id.id,
                            'name': search_product_code.product_id.name,
                            'product_uom': search_product_code.unit.id,
                            'product_uom_qty': 1,
                            'price_unit': set_price,
                            'is_warehouse': True,
                           'warehouses_id':search_product_code.product_id.sale_warehouse_id.id,
                            'sh_sale_barcode_scanner_is_last_scanned': is_last_scanned,
                            'sequence': sequence,
                        }
                        if search_product_code.unit:
                            vals.update({
                                "product_uom": search_product_code.unit.id,
                            })
                        new_order_line = self.order_line.new(vals)
                        new_order_line.write({
                          'warehouses_id':search_product_code.product_id.sale_warehouse_id.id,

                        })
                        self.order_line += new_order_line

                else:
                    raise UserError(
                        _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

    # def on_barcode_scanned(self, barcode):
    #     self._add_product(barcode)
