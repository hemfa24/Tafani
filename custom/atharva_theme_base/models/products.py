# -*- coding: utf-8 -*-

import datetime
from datetime import timedelta

from odoo.tools.translate import html_translate
from odoo.osv import expression
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_rating = fields.Float(string='Product Rating', compute='_compute_product_rating', store=True)
    hover_image = fields.Image("Hover Image", max_width=512, max_height=512)
    product_tab_description = fields.Html(string="Description Tab", translate=html_translate)
    doc_name = fields.Char(string="Document Name", default='Documents', required=True)
    is_active_doc = fields.Boolean(default=False, string='Show Document')
    doc_attachments = fields.Many2many("ir.attachment", string="Documents")
    is_unavailable_in_stock = fields.Boolean(string='Unavailable in Stock', compute='available_stock', store=True)
    have_color_attribute = fields.Boolean(string='Color Attribute', default=False, compute='is_contains_color_attribute', store=True)

    @api.depends('attribute_line_ids')
    def is_contains_color_attribute(self):
        for product in self:
            for ptal in product.valid_product_template_attribute_line_ids:
                if ptal.attribute_id.display_type == 'color':
                    product.have_color_attribute = True
                else:
                    product.have_color_attribute = False

    @api.depends('virtual_available', 'allow_out_of_stock_order', 'detailed_type')
    def available_stock(self):
        for product in self:
            if product.detailed_type == 'product' and not product.allow_out_of_stock_order and product.virtual_available < 1:
                product.is_unavailable_in_stock = True
            else:
                product.is_unavailable_in_stock = False

    @api.model_create_multi
    def create(self, vals_lst):
        for vals in vals_lst:
            if vals.get('doc_attachments'):
                doc_list = [i for i in vals['doc_attachments'][0][2]]
                attachments = self.env['ir.attachment'].sudo().browse(doc_list)
                for record in attachments:
                    if record.id in doc_list:
                        if record.public == False:
                            record.public = True
        res = super(ProductTemplate, self).create(vals_lst)
        return res

    def write(self, vals):
        if vals.get('doc_attachments'):
            doc_list = [i for i in vals['doc_attachments'][0][2]]
            attachments = self.env['ir.attachment'].sudo().browse(doc_list)
            for record in attachments:
                if record.id in doc_list:
                    if record.public == False:
                        record.public = True
        return super(ProductTemplate, self).write(vals)

    @api.depends('message_ids')
    def _compute_product_rating(self):
        ''' Compute product rating '''
        for i in self:
            prodRating = round(i.sudo().rating_get_stats().get('avg') / 1 * 100) / 100
            i.product_rating = prodRating

    def _get_best_seller_product(self, from_date, website_id, limit ):
        self.env.cr.execute("""SELECT PT.id, SUM(SO.product_uom_qty),PT.website_id
                                    FROM sale_order S
                                    JOIN sale_order_line SO ON (S.id = SO.order_id)
                                    JOIN product_product P ON (SO.product_id = P.id)
                                    JOIN product_template pt ON (P.product_tmpl_id = PT.id)
                                    WHERE S.state in ('sale','done')
                                    AND (S.date_order >= %s AND S.date_order <= %s)
                                    AND (PT.website_id IS NULL OR PT.website_id = %s)
                                    AND PT.active='t'
                                    AND PT.is_published='t'
                                    GROUP BY PT.id
                                    ORDER BY SUM(SO.product_uom_qty)
                                    DESC LIMIT %s
                                """, [datetime.datetime.today() - timedelta(from_date), datetime.datetime.today(), website_id, limit])
        table = self.env.cr.fetchall()
        products = []
        for record in table:
            if record[0]:
                pro_obj = self.env[
                    'product.template'].sudo().browse(record[0])
                if pro_obj.sale_ok == True and pro_obj.is_published == True:
                    products.append(pro_obj)
        return products

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)
        if res.get('has_discounted_price', False):
            per = 100 - ((res['price'] /  res['list_price']) * 100)
            res.update({'as_offer_discount': "{:.2f}".format(per)})
        return res

    @api.model
    def _search_build_domain(self, domain_list, search, fields, extra=None):
        res = super(ProductTemplate, self)._search_build_domain(domain_list, search, fields, extra)
        new_domain = [res]
        if self.env.context.get('brands',[]) != []:
            new_domain.append([('product_brand_id', 'in', [int(b) for b in self.env.context['brands']])])
        if self.env.context.get('rating',[]) != []:
            new_domain.append([('product_rating', '>=', max([int(b) for b in self.env.context['rating']]))])
        if self.env.context.get('tags',[]) != []:
            new_domain.append([('product_tag_ids', 'in', [int(b) for b in self.env.context['tags']])])
        if self.env.context.get('only_stock',False):
            new_domain.append([('is_unavailable_in_stock', '=', False)])
        res = expression.AND(new_domain)
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_offer_timing(self, pricelist):
        common_domain = [('date_end','!=',False), ('show_timer','=',True)]
        check_global = pricelist.item_ids.search([('applied_on','=','3_global')] + common_domain, limit=1)
        check_category = pricelist.item_ids.search([('applied_on','=','2_product_category'),('categ_id','=',self.categ_id.id)] + common_domain, limit=1)
        check_product_tmpl = pricelist.item_ids.search([('applied_on','=','1_product'),('product_tmpl_id','=',self.product_tmpl_id.id)] + common_domain, limit=1)
        check_product_varient = pricelist.item_ids.search([('applied_on','=','0_product_variant'), ('product_id','=',self.id)] + common_domain, limit=1)
        if check_product_varient:
            return check_product_varient.date_end
        elif check_product_tmpl:
            return check_product_tmpl.date_end
        elif check_category:
            return check_category.date_end
        elif check_global:
            return check_global.date_end
        return False

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    pv_thumbnail = fields.Image('Variant Image')
