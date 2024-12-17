# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_line_ids = fields.One2many(
        related='product_variant_ids.barcode_line_ids', readonly=False, ondelete="cascade")

    uom_category_id = fields.Many2one(
        "uom.category",
        "UOM Category",
        related="uom_id.category_id"
    )

    @api.constrains('barcode', 'barcode_line_ids')
    def check_uniqe_name(self):
        for rec in self:
            if self.env.company and self.env.company.sh_multi_barcode_unique:
                multi_barcode_id = self.env['product.template.barcode'].search([('name', '=', rec.barcode)])
                if multi_barcode_id:
                    raise ValidationError(_(
                        'Barcode must be unique!'))

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        templates = super(ShProductTemplate, self).create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('barcode_line_ids'):
                related_vals['barcode_line_ids'] = vals['barcode_line_ids']
            if related_vals:
                template.write(related_vals)
        return templates

    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)


class ShProduct(models.Model):
    _inherit = 'product.product'

    barcode_line_ids = fields.One2many(
        'product.template.barcode', 'product_id', 'Barcode Lines', ondelete="cascade")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        res = super(ShProduct, self)._name_search(name=name, args=args,
                                                  operator=operator, limit=limit, name_get_uid=name_get_uid)
        mutli_barcode_search = list(self._search(
            [('barcode_line_ids', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
        if mutli_barcode_search:
            return res + mutli_barcode_search
        return res

    @api.constrains('barcode', 'barcode_line_ids')
    def check_uniqe_name(self):
        for rec in self:
            if self.env.company and self.env.company.sh_multi_barcode_unique:
                multi_barcode_id = self.env['product.template.barcode'].search([('name', '=', rec.barcode)])
                if multi_barcode_id:
                    raise ValidationError(_(
                        'Barcode must be unique!'))

    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)


import re


class ShProductBarcode(models.Model):
    _name = 'product.template.barcode'
    _description = "Product Barcode"

    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade")
    name = fields.Char("Barcode", required=True, ondelete="cascade")
    price = fields.Float("Price")
    available_item = fields.Boolean('Valuable Sale & POS', store=True)
    unit = fields.Many2one('uom.uom', 'Secondary UOM', required=True)
    price_lst = fields.Many2one('product.pricelist', required=True)
    negative_qty_price = fields.Boolean('Allow Negative Quantity & Price', store=True)
    item_pricelist_id = fields.Many2one('product.pricelist.item')

    def create_update_price_item(self, item_pricelist_id=False, context=None):
        context = dict(self.env.context or (context or {}))
        if not context.get('updating_price', False):
            item_vals = {
                'product_id': self.product_id.id,
                'uom_id': self.unit.id,
                'multi_barcode': self.name,
                'pricelist_id': self.price_lst.id,
                'fixed_price': self.price,
                'applied_on': '0_product_variant',
                'compute_price': 'fixed',
            }
            item_pricelist_id_2 = self.env['product.pricelist.item'].sudo().search([('multi_barcode', '=', self.name)])
            if item_pricelist_id:
                item_pricelist_id.with_context({'updating_price': True}).write(item_vals)

            elif item_pricelist_id_2:
                for rec in item_pricelist_id_2:
                    if rec:
                        rec.with_context({'updating_price': True}).write(item_vals)
            else:
                item_pricelist_id = self.env['product.pricelist.item'].with_context({'updating_price': True}).create(item_vals)
                self.item_pricelist_id = item_pricelist_id.id

        return True

    @api.model
    def create(self, vals):
        res = super().create(vals)
        context = dict(self.env.context or {})
        for rec in res:
            if rec.price_lst:
                if not context.get('updating_price', False):
                    rec.create_update_price_item()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        context = dict(self.env.context or {})
        if self._context.get('params'):
            if self._context['params'].get('model') != 'product.pricelist.item':
                for rec in self:
                    if rec.price_lst:
                        rec.create_update_price_item(rec.item_pricelist_id, context=self._context)
        else:
            if not context.get('updating_price', False):
                 for rec in self:
                    if rec.price_lst:
                        rec.create_update_price_item(rec.item_pricelist_id, context=self._context)
        return res

    def unlink(self):
        for rec in self:
            if rec.item_pricelist_id and not rec.env.context.get('force_delete', False):
                rec.item_pricelist_id.with_context(force_delete=True).unlink()
        return super().unlink()

    @api.constrains('name')
    def check_uniqe_name(self):
        for rec in self:
            product_id = self.env['product.product'].sudo().search(
                ['|', ('barcode', '=', rec.name), ('barcode_line_ids.name', '=', rec.name),
                 ('id', '!=', rec.product_id.id)])
            if product_id:
                raise ValidationError(_('Barcode must be unique!'))

            product_id_2 = self.env['product.product'].sudo().search(
                [('barcode', '=', rec.name)])
            if product_id_2:
                raise ValidationError(_('Barcode must be unique!'))
            else:
                barcode_id = self.env['product.template.barcode'].search(
                    [('name', '=', rec.name), ('id', '!=', rec.id)])
                if barcode_id:
                    raise ValidationError(_('Barcode must be unique!'))

    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)

    @api.model
    def sh_create_from_pos(self, vals):
        id = self.create(vals)
        return id.read()

class ShProductPriceListItem(models.Model):
        _inherit = 'product.pricelist.item'

        dynamic_price_ids = fields.One2many("product.template.barcode", "item_pricelist_id", 'Dynamic Products Barcode')

        def create_update_price_item(self, item_pricelist_id=False):
            context = dict(self.env.context or {})
            item_vals = {
                'price': self.fixed_price,
                'unit': self.uom_id.id,
                'product_id': self.product_id.id,
            }
            item_pricelist_id = self.env['product.template.barcode'].sudo().search([('item_pricelist_id', '=', self.id)])
            barcode_pricelist_id = self.env['product.template.barcode'].sudo().search(
                [('name', '=', self.multi_barcode)])
            if item_pricelist_id:
                item_pricelist_id.with_context({'updating_price': True}).write(item_vals)
            if barcode_pricelist_id:
                barcode_pricelist_id.with_context({'updating_price': True}).write(item_vals)
            return True

        @api.model
        def write(self, vals):
            res = super().write(vals)
            if self._context.get('params'):
                if self._context['params'].get('model') != 'product.product':
                    for rec in self:
                        rec.create_update_price_item()
            else:  # If 'params' key is not present
                self.create_update_price_item()
            return res


        def unlink(self):
            for rec in self:
                if rec.dynamic_price_ids and not rec.env.context.get('force_delete', False):
                    rec.dynamic_price_ids.with_context(force_delete=True).unlink()
            return super().unlink()
