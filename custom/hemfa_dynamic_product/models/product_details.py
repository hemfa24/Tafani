# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_details(self, barcode):
        check_barcode = barcode
        # product_details = self.search([('barcode', '=', check_barcode)])

        product_barcode = self.env['product.template.barcode'].sudo().search(
            [('name', '=', check_barcode),
             ('available_item', '=', True)
             ], limit=1)
        # prod_barcode_id = self.barcode_ids.search([('barcode', '=', check_barcode)], limit=1)

        if product_barcode:
            product_details = product_barcode.product_id
        # elif prod_barcode_id:
        #     product_details = prod_barcode_id.product_id
        else:
            product_details = self.search([('barcode', '=', check_barcode)])

        if product_details:
            print(product_details)
            # price = self.env['account.tax']._fix_tax_included_price_company(self.env['sale.order.line'].search([],limit=1).sudo()._get_display_price(product_details), self.env['account.tax'], self.env['account.tax'], self.env.company)
            type_list = []
            price1 = False
            prod_unit1 = False
            has_currency_price1 = False
            price2 = False
            prod_unit2 = False
            has_currency_price2 = False
            product_price1 = self.env['product.pricelist.item'].sudo().search(
                [('product_id', '=', product_details.id)], limit=1)
            print(product_price1)
            if product_price1:
                type_list.append(product_price1.uom_id.id)
                price1 = product_price1.fixed_price or product_price1.price
                # price1 = round(price1,2) if price1 else False
                price1 = str(price1) if price1 else False
                prod_unit1 = product_price1.uom_id.name
                has_currency_price1 = True if not price1 else False
            product_price2 = self.env['product.pricelist.item'].sudo().search(
                [('product_id', '=', product_details.id), ('uom_id', 'not in', type_list)], limit=1)
            print(product_price2)
            if product_price2:
                type_list.append(product_price2.uom_id.id)
                price2 = product_price2.fixed_price or product_price2.price
                # price2 = round(price2,2) if price2 else False
                price2 = str(price2) if price2 else False
                prod_unit2 = product_price2.uom_id.name
                has_currency_price2 = True if not price2 else False
            return product_details.id, product_details.name, price1 or round(product_details.list_price, 2), prod_unit1, product_details.barcode, product_details.default_code, product_details.categ_id.name, product_details.currency_id.symbol, price2, prod_unit2, has_currency_price1, has_currency_price2
        else:
            return "Not Found", "المنتج غير مسجل", False, False, "Not Found", "Not Found", "Not Found", False, False, False, False, False
