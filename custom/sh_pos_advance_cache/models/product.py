# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSession,
                       self)._loader_params_product_product()
        result['search_params']['fields'].extend(["barcode_line_ids"])
        return result

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(PosSession, self)._pos_ui_models_to_load()
        models_to_load.remove('product.product')
        models_to_load.remove('res.partner')
        return models_to_load

    def sh_load_model(self, Model):
            return self._load_model(Model)

class PosConfig(models.Model):
    _inherit = "pos.config"

    sh_product_upate = fields.Selection([('online','Real Time'),('on_refresh','On Refresh')],
        string="Update Product ",default='on_refresh')

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    sh_product_upate = fields.Selection(
        related="pos_config_id.sh_product_upate", readonly=False)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def toggle_active(self):
        res = super(ProductTemplate, self).toggle_active()
        for rec in self:
            if rec.active==False:
                for line in rec.product_variant_ids:
                    self.env['product.update'].sudo().create({'delete_ids':str(line.id)})
                    self.env['product.update'].broadcast_product(line)

            if rec.active==True:
                for line in rec.product_variant_ids:
                    delete_ids = self.env['product.update'].sudo().search([('delete_ids','=',str(line.id))])
                    if delete_ids:
                        delete_ids.sudo().unlink()
                    self.env['product.update'].broadcast_product(line)

        return res



    def write(self, vals):

        if 'active' in vals and vals.get('active')==False:
            for rec in self:
                for line in rec.product_variant_ids:
                    self.env['product.update'].sudo().create({'delete_ids':str(line.id)})

        res = super(ProductTemplate, self).write(vals)

        for rec in self:
            if rec.available_in_pos and rec.active:
                for line in rec.product_variant_ids:
                    delete_ids = self.env['product.update'].sudo().search([('delete_ids','=',str(line.id))])
                    if delete_ids:
                        delete_ids.sudo().unlink()
                    self.env['product.update'].broadcast_product(line)
        return res

    def unlink(self):
        for rec in self:
            for line in rec.product_variant_ids:
                self.env['product.update'].sudo().create({'delete_ids':str(line.id)})
        res = super(ProductTemplate, self).unlink()
        return res

class Product(models.Model):
    _inherit = 'product.product'

    def toggle_active(self):
        res = super(Product, self).toggle_active()
        for rec in self:
            if rec.active==False:
                self.env['product.update'].sudo().create({'delete_ids':str(rec.id)})
                self.env['product.update'].broadcast_product(rec)
            if rec.active==True:
                delete_ids = self.env['product.update'].sudo().search([('delete_ids','=',str(rec.id))])
                if delete_ids:
                    delete_ids.sudo().unlink()
                self.env['product.update'].broadcast_product(rec)

        return res

    @api.model
    def create(self, vals):
        res = super(Product, self).create(vals)
        if res.id:
            self.env['product.update'].broadcast_product(res)
        return res

    def write(self, vals):
        if 'active' in vals and vals.get('active')==False:
            for rec in self:
                self.env['product.update'].sudo().create({'delete_ids':str(rec.id)})

        if 'active' in vals and vals.get('active')==True:
            for rec in self:
                delete_ids = self.env['product.update'].sudo().search([('delete_ids','=',str(rec.id))])
                if delete_ids:
                    delete_ids.sudo().unlink()
                self.env['product.update'].broadcast_product(rec)

        res = super(Product, self).write(vals)
        for rec in self:
            if rec.available_in_pos and rec.active:
                self.env['product.update'].broadcast_product(rec)
        return res

    def unlink(self):
        for rec in self:
            last_id = self.env['product.update'].sudo().search([])
            self.env['product.update'].sudo().create({'delete_ids':str(rec.id)})
        res = super(Product, self).unlink()
        return res
    #



class PosStockChannel(models.Model):
    _name = 'product.update'

    delete_ids = fields.Char("Delete Ids")

    def _get_pos_ui_product_category(self, params):
        categories = self.env['product.category'].search_read(**params['search_params'])
        category_by_id = {category['id']: category for category in categories}
        for category in categories:
            category['parent'] = category_by_id[category['parent_id'][0]] if category['parent_id'] else None
        return categories

    def _loader_params_product_category(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'parent_id']}}

    def broadcast_product(self, product):
        if product.id:
            fields = ['display_name', 'lst_price', 'standard_price', 'categ_id',
                      'pos_categ_id', 'taxes_id','barcode', 'default_code', 'to_weight', 'uom_id',
                      'description_sale', 'description', 'product_tmpl_id','tracking',
                      'write_date', 'available_in_pos', 'attribute_line_ids', 'active', 'name', 'qty_available', 'barcode_line_ids']
            if 'optional_product_ids' in self.env['product.product']._fields:
                fields.append('optional_product_ids')
            if 'sh_minimum_qty_pos' in self.env['product.product']._fields:
                fields.append('sh_minimum_qty_pos')
            if 'sh_multiples_of_qty' in self.env['product.product']._fields:
                fields.append('sh_multiples_of_qty')
            if 'sh_qty_in_bag' in self.env['product.product']._fields:
                fields.append('sh_qty_in_bag')
            if 'sh_product_non_returnable' in self.env['product.product']._fields:
                fields.append('sh_product_non_returnable')
            if 'sh_product_non_exchangeable' in self.env['product.product']._fields:
                fields.append('sh_product_non_exchangeable')
            if 'sh_select_user' in self.env['product.product']._fields:
                fields.append('sh_select_user')
            if 'barcode_line_ids' in self.env['product.product']._fields:
                fields.append('barcode_line_ids')
            if 'sh_alternative_products' in self.env['product.product']._fields:
                fields.append('sh_alternative_products')
            if 'suggestion_line' in self.env['product.product']._fields:
                fields.append('suggestion_line')
            if 'sh_bundle_product_ids' in self.env['product.product']._fields:
                fields.append('sh_bundle_product_ids')
            if 'sh_is_bundle' in self.env['product.product']._fields:
                fields.append('sh_is_bundle')
            if 'sh_amount_total' in self.env['product.product']._fields:
                fields.append('sh_amount_total')
            if 'sh_secondary_uom' in self.env['product.product']._fields:
                fields.append('sh_secondary_uom')
            if 'sh_is_secondary_unit' in self.env['product.product']._fields:
                fields.append('sh_is_secondary_unit')
            if 'sh_product_tag_ids' in self.env['product.product']._fields:
                fields.append('sh_product_tag_ids')

            data = product.read(fields)
            name = product.name + ': ' + ', '.join(product.product_template_attribute_value_ids.mapped('display_name'))
            data[0].update({
                'name': name,
                'display_name': name,
            })
            if data and len(data) > 0:
                pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
                if pos_session:
                    categories = self._get_pos_ui_product_category(self._loader_params_product_category())
                    product_category_by_id = {category['id']: category for category in categories}
                    for each_data in data:
                        each_data['categ'] = product_category_by_id[each_data['categ_id'][0]]
                    for each_session in pos_session:
                        self.env['bus.bus']._sendmany(
                            [[each_session.user_id.partner_id, 'product_update', data]])


class ProductBundle(models.Model):
    _inherit = 'sh.product.bundle'

    def unlink(self):
        res = super().unlink()
        self.update_bundle()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        self.update_bundle()
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self.update_bundle()
        return res

    def update_bundle(self):
        bundle_product_data = self.search_read([])
        bundle_product_data_by_id = {}
        if bundle_product_data and len(bundle_product_data) > 0:
            for each_bundle in bundle_product_data:
                if each_bundle.get('sh_bundle_id'):
                    each_bundle['sh_bundle_id'] = each_bundle['sh_bundle_id'][0]
                if each_bundle.get('sh_product_id'):
                    each_bundle['sh_product_id'] = each_bundle['sh_product_id'][0]
                if each_bundle.get('sh_uom'):
                    each_bundle['sh_uom'] = each_bundle['sh_uom'][0]
            pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
            if pos_session:
                for each_session in pos_session:
                    self.env['bus.bus']._sendmany(
                        [[each_session.user_id.partner_id, 'product_bundle_update', bundle_product_data]])

class ProductTemplateBarcode(models.Model):
    _inherit = 'product.template.barcode'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self.update_barcode()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if vals.get('price_lst', False):
            self.delete_barcode()
        self.update_barcode()
        return res

    @api.model
    def unlink(self):
        self.delete_barcode()
        res = super().unlink()
        self.update_barcode()
        return res

    def update_barcode(self):
        pos_session = self.env['pos.session'].search(
            [('state', 'in', ['opened', 'opening_control'])])
        if pos_session:
            for each_session in pos_session:
                barcode_product_data = self.search_read([
                    ('available_item','=','t'), ('price_lst', 'in', each_session.config_id.available_pricelist_ids.ids)
                ],['product_id', 'name','create_date','price','available_item','unit','price_lst','negative_qty_price'])
                barcode_product_data_by_id = {}
                if barcode_product_data and len(barcode_product_data) > 0:
                    for each_data in barcode_product_data:
                        if each_data.get('product_id'):
                            each_data['product_id'] = each_data['product_id'][0]
                    barcode_product_data_by_id = {
                    data['id']: data for data in barcode_product_data}

                if barcode_product_data_by_id:
                    self.env['bus.bus']._sendmany(
                        [[each_session.user_id.partner_id, 'product_barcode_update', barcode_product_data_by_id]])

    def delete_barcode(self):
        barcode_product_data = self
        barcode_product_data_by_id = {}
        if barcode_product_data and len(barcode_product_data) > 0:

            pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
            if pos_session:
                for each_session in pos_session:
                    for each_data in barcode_product_data:
                        if each_data.price_lst.id not in  each_session.config_id.available_pricelist_ids.ids:
                            barcode_product_data_by_id.update({
                                each_data.id: {'id': each_data.id}
                            })
                    if barcode_product_data_by_id:
                        self.env['bus.bus']._sendmany(
                            [[each_session.user_id.partner_id, 'product_barcode_delete', barcode_product_data_by_id]])

class ProductTemplateBarcode(models.Model):
    _name = 'product.template.barcode.update'

    delete_ids = fields.Char("Delete Ids")

    def broadcast_product_barcode(self, product):
        if product.id:
            fields = ['product_id', 'name','create_date']
            data = product.read(fields)
            if data and len(data) > 0:
                pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
                if pos_session:
                    for each_data in data:
                        each_data['product_id'] = each_data['product_id'][0]
                    for each_session in pos_session:
                        self.env['bus.bus']._sendmany(
                            [[each_session.user_id.partner_id, 'product_barcode_update', data]])

class ProductSuggestion(models.Model):
    _inherit = 'product.suggestion'

    def unlink(self):
        res = super().unlink()
        self.update_suggestion()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        self.update_suggestion()
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self.update_suggestion()
        return res

    def update_suggestion(self):
        suggested_product_data = self.search_read([],['id','product_id','product_suggestion_id'])
        suggested_product_data_by_id = {}
        if suggested_product_data and len(suggested_product_data) > 0:
            for each_suggestion in suggested_product_data:
                if each_suggestion.get('product_suggestion_id'):
                    each_suggestion['product_suggestion_id'] = each_suggestion['product_suggestion_id'][0]
            suggested_product_data_by_id = {
            data['id']: data for data in suggested_product_data}
            pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
            if pos_session:
                for each_session in pos_session:
                    self.env['bus.bus']._sendmany(
                        [[each_session.user_id.partner_id, 'product_suggestion_update', suggested_product_data_by_id]])

class ProductTag(models.Model):
    _inherit = 'sh.product.tag'

    def unlink(self):
        res = super().unlink()
        self.update_tag()
        return res


    def write(self, vals):
        res = super(ProductTag, self).write(vals)
        self.update_tag()
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(ProductTag, self).create(vals)
        self.update_tag()
        return res

    def update_tag(self):
        product_tag_data = self.search_read([])
        product_tag_data_by_id = {}
        if product_tag_data and len(product_tag_data) > 0:
            pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
            if pos_session:
                for each_session in pos_session:
                    self.env['bus.bus']._sendmany(
                        [[each_session.user_id.partner_id, 'product_tag_update', product_tag_data]])

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    def unlink(self):
        self.update_pricelist_delete()
        res = super().unlink()
        self.update_pricelist()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.update_pricelist()
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        self.update_pricelist()
        return res

    def update_pricelist(self):
        product_pricelist_data = self.search_read([('id','in',self.ids)])
        pos_session = self.env['pos.session'].search(
                [('state', 'in', ['opened', 'opening_control'])])
        if pos_session:
            for each_session in pos_session:
                self.env['bus.bus']._sendmany(
                    [[each_session.user_id.partner_id, 'product_pricelist_item_update', product_pricelist_data]])



#
    def update_pricelist_delete(self):
        data_list = []
        for rec in self:
            product_pricelist_data = {'id':rec.id,'product_id':rec.product_id.id,'product_tmpl_id':rec.product_tmpl_id.id}
            data_list.append(product_pricelist_data)

        pos_session = self.env['pos.session'].search(
                [('state', 'in', ['opened', 'opening_control'])])
        if pos_session:
            for each_session in pos_session:
                self.env['bus.bus']._sendmany(
                    [[each_session.user_id.partner_id, 'product_pricelist_item_delete', data_list]])

class StockQuantity(models.Model):
    _inherit = 'stock.quant'

    def write(self, vals):
        res = super().write(vals)
        self.env['product.update'].broadcast_product(self.product_id)
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        return res
