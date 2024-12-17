# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo.exceptions import ValidationError, AccessError
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang

class PriceListItemForm(models.Model):
    _inherit = 'product.pricelist'

    multi_barcode = fields.Char('Barcode ?')


    def write(self, vals):
        res = super(PriceListItemForm, self).write(vals)
        for rec in self.item_ids:
                rec.deco_value=1
        return res
    

    @api.onchange('multi_barcode')
    def _onchange_multi_barcode(self):
        for record in self:
            for dec in record.item_ids:
                dec.deco_value=1
            obj = self.env["product.template.barcode"].sudo().search(
                [('name', '=', record.multi_barcode),
                 ], limit=1)
            if obj:
                for line in record.item_ids:
                    if line.product_id.id == obj.product_id.id and line.uom_id.id == obj.unit.id:
                        line.deco_value = 0
            record.multi_barcode=False


class PriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    multi_barcode = fields.Char('Barcode ?')

    deco_value =  fields.Integer(default=1,string = 'dec val')
    

    @api.onchange('multi_barcode')
    def _onchange_multi_barcode(self):
        for record in self:
            if record.multi_barcode:
                product_details = self.env["product.product"].sudo().search([('barcode', '=', record.multi_barcode)])
                obj = self.env["product.template.barcode"].sudo().search(
                    [('name', '=', record.multi_barcode),
                    ('available_item', '=', True)
                    ], limit=1)
                if obj:
                    record.product_id = obj.product_id
                    record.uom_id = obj.unit
                elif product_details :
                    record.product_id = product_details.id
                    record.uom_id = product_details.uom_id
                else:
                    if record.applied_on == '0_product_variant':
                        raise ValidationError(
                            _('You cannot add a Product Not available.'))

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _compute_name_and_price(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s") % (
                    item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s") % (item.product_id.with_context(
                    display_default_code=False).display_name)
            elif item.product_id and item.applied_on == '4_barcode':
                item.name = _("Dynamic Product: %s") % (
                    item.product_id.with_context(display_default_code=False).display_name)
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                item.price = formatLang(
                    item.env, item.fixed_price, monetary=True, dp="Product Price", currency_obj=item.currency_id)
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount", item.percent_price)
            else:
                item.price = _("%(percentage)s %% discount and %(price)s surcharge",
                               percentage=item.price_discount, price=item.price_surcharge)
