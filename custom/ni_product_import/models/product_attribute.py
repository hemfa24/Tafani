# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('from_import', True):
            auto_gen_variant = True
        else:
            auto_gen_variant = self.env['ir.config_parameter'].sudo().get_param('ni_prod_import.auto_gen_variant')
        return super(ProductTemplateAttributeLine, self.with_context(
            update_product_template_attribute_values=auto_gen_variant,
            skip_log=True)).create(vals_list)

    def write(self, vals):
        if self.env.context.get('from_import', True):
            auto_gen_variant = True
        else:
            auto_gen_variant = self.env['ir.config_parameter'].sudo().get_param('ni_prod_import.auto_gen_variant')
        return super(ProductTemplateAttributeLine, self.with_context(
            update_product_template_attribute_values=auto_gen_variant,
            skip_log=True)).write(vals)
