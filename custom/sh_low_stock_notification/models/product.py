# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    minimum_quantity = fields.Float(
        compute='_compute_minimum_quantity', store=True, inverse='_inverse_set_minimum_quantity')

    def _inverse_set_minimum_quantity(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.minimum_quantity = template.minimum_quantity

    @api.depends('product_variant_ids', 'product_variant_ids.minimum_quantity')
    def _compute_minimum_quantity(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.minimum_quantity = template.product_variant_ids.minimum_quantity
        for template in (self - unique_variants):
            template.minimum_quantity = 0.0


class Product(models.Model):
    _inherit = 'product.product'

    minimum_quantity = fields.Float(index=True)

    @api.model
    def create(self, vals):
        template_id = self.env['product.template'].sudo().browse(
            vals.get('product_tmpl_id'))
        if template_id:
            minimum_qty = template_id.minimum_quantity
            if vals.get('product_template_attribute_value_ids') and len(vals.get('product_template_attribute_value_ids')[0][2]) == 0:
                vals.update({
                    'minimum_quantity': minimum_qty
                })
        res = super(Product, self).create(vals)
        if vals.get('minimum_quantity'):
            comp_id = self.env.company.id
            val = {'product_id': res.id, 'company_id': comp_id,
                   'minimum_qty': vals.get('minimum_quantity')}
            self.env['res.company.product'].create(val)
        return res

    def write(self, values):
        res = super(Product, self).write(values)
        if values.get('minimum_quantity'):
            for rec in self:
                comp_id = self.env.company.id
                comp_prod_obj = self.env['res.company.product'].search(
                    [('product_id', '=', rec.id), ('company_id', '=', comp_id)], limit=1)

                if comp_prod_obj:  # if entry for this product and company exist than update

                    if not comp_prod_obj.minimum_qty == values.get('minimum_quantity'):
                        comp_prod_obj.minimum_qty = values.get(
                            'minimum_quantity')

                else:  # create new entry for this product and company

                    vals = {'product_id': rec.id, 'company_id': comp_id,
                            'minimum_qty': values.get('minimum_quantity')}
                    self.env['res.company.product'].create(vals)

        return res
