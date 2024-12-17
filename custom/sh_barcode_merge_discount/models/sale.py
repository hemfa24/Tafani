# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Fully Override to resolve issue for discount on Sales order line
    @api.onchange('product_id', 'product_tmpl_id', 'product_uom_qty')
    def on_product_id_barcode(self):
        for rec in self:
            if not rec.is_make_lock_price_unit and rec.order_id.discount_type != 'global':
                pricelist_id = rec.order_id.pricelist_id if rec.order_id else False
                if not pricelist_id:
                    pricelist_id = self.env['product.pricelist'].search([], limit=1)
                print("pricelist_id", pricelist_id)
                print("rec.product_id.id", rec.product_id.id, rec.product_template_id)
                print("rec.uom_id.id", rec.product_id.uom_id.id)
                # product_tmpl_id

                rec.product_uom = rec.product_id.uom_id.id if rec.product_id.uom_id else False
                obj_price_stand = self.env['product.pricelist.item'].sudo().search([
                    ('product_id', '=', rec.product_id.id),
                    ('uom_id', '=', rec.product_id.uom_id.id),
                    ('pricelist_id', '=', pricelist_id.id)
                ], limit=1)
                if obj_price_stand:
                    rec.price_unit = obj_price_stand.fixed_price
                else:
                    rec.price_unit = rec.product_id.list_price
