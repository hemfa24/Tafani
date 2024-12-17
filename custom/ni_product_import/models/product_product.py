# -*- coding: utf-8 -*-

from odoo import api, fields, models


class posProductBrand(models.Model):
    _name = 'pos.product.brand'

    name = fields.Char()


class productModel(models.Model):
    _name = 'product.model'

    name = fields.Char()


class productSex(models.Model):
    _name = 'product.sex'

    name = fields.Char()


class productCollege(models.Model):
    _name = 'product.college'

    name = fields.Char()


class CollectionsCollections(models.Model):
    _name = 'product.collections'

    name = fields.Char()


class SeasonalitySeasonality(models.Model):
    _name = 'seasonality.seasonality'

    name = fields.Char()


class ProductTypeGroup(models.Model):
    _name = 'product.type.group'

    name = fields.Char()


class AgeGroup(models.Model):
    _name = 'age.group'

    name = fields.Char()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    import_unique_code = fields.Char('Import Code NO')
    product_brand_id = fields.Many2one('pos.product.brand')
    model_id = fields.Many2one('product.model')
    sex_id = fields.Many2one('product.sex')
    college_id = fields.Many2one('product.college')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    nex_text_cells = fields.Char('Nex Text Cells')
    model_no = fields.Char('ModelNber')
    material_composition = fields.Char('Material Composition')
    age_group_id = fields.Many2one('age.group', 'Age Group')
    product_type_group_id = fields.Many2one('product.type.group', 'Product Type Group')
    collection_id = fields.Many2one('product.collections', 'Collections')
    seasonality_id = fields.Many2one('seasonality.seasonality', 'Seasonality')

    # is_gen_variant = fields.Boolean(string='generate variant', default=True)

    # def _create_variant_ids(self):
    #     auto_gen_variant = self.env['ir.config_parameter'].sudo().get_param('ni_prod_import.auto_gen_variant')
    #     if auto_gen_variant:
    #         return super(ProductProduct, self)._create_variant_ids()
    #     return True
    #

    # @api.model_create_multi
    # def create(self, vals_list):
    #
    #     products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
    #     return products

    # def clear_caches(self):
    #     return False
    #     # if "without_clear_caches" not in self._context:
    #     #     return super(ProductProduct, self).clear_caches()

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        self.clear_caches()
        return products

    def write(self, values):
        res = super().write(values)
        self.clear_caches()
        return res
