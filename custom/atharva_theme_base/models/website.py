# -*- coding: utf-8 -*-

import json
import re

from odoo import fields, models, api
from odoo.tools.translate import html_translate


class ShopProductPerPage(models.Model):
    _name = 'as.ppg'
    _description = "Product Per Page Dropdown Shop"
    _order = "sequence,id"

    sequence = fields.Integer(string="Sequence")
    name = fields.Integer(string="PPG", default='10', required=True)

    _sql_constraints = [("name_uniqe", "unique (name)", "Value already exists.!")]

class CustomWebsite(models.Model):
    _inherit = 'website'

    shop_special_offer = fields.Html(sanitize_form=False, sanitize_attributes=False, translate=html_translate)

    # Globel Settings
    active_login_popup = fields.Boolean(string="Login Popup")
    active_mini_cart = fields.Boolean(string="Mini Cart", default=True)
    active_scroll_top = fields.Boolean(string="Scroll Top", default=True)
    active_b2b_mode = fields.Boolean(string="B2B Mode", default=False)

    # Shop Page Settings
    active_shop_quick_view = fields.Boolean(string="Quick View", default=True)
    active_shop_rating = fields.Boolean(string="Rating")
    active_shop_similar_product = fields.Boolean(string="Similar Product", default=True)
    active_shop_offer_timer = fields.Boolean(string="Offer timer", default=True)
    active_shop_stock_info = fields.Boolean(string="Stock Info", default=True)
    active_shop_color_variant = fields.Boolean(string="Color Variant", default=True)
    active_shop_brand_info = fields.Boolean(string="Brand Info", default=True)
    active_shop_hover_image = fields.Boolean(string="Hover Image", default=True)
    active_shop_label = fields.Boolean(string="Shop Label", default=True)
    active_shop_clear_filter = fields.Boolean(string="Shop Clear Filter", default=True)
    active_shop_ppg = fields.Boolean(string="Shop PPG", default=True)
    active_attribute_search = fields.Boolean(string="Shop Attribute Search", default=True)
    active_stock_only = fields.Boolean(string="Shop Stock Only", default=True)
    active_load_more = fields.Boolean(string="Shop Load More", default=True)
    active_tag_filter = fields.Boolean(string="Shop Tag Filter", default=True)
    active_brand_filter = fields.Boolean(string="Shop Brand Filter", default=True)
    active_rating_filter = fields.Boolean(string="Shop Brand Filter", default=True)
    active_attribute_count = fields.Boolean(string="Shop Attribute Counter", default=True)

    # Product Detail Setting
    active_product_label = fields.Boolean(string="Product Label", default=True)
    active_product_offer_timer = fields.Boolean(string="Product Offer Timer", default=True)
    active_product_reference = fields.Boolean(string="Product Reference", default=True)
    active_product_tag = fields.Boolean(string="Product Tag", default=True)
    active_product_brand = fields.Boolean(string="Product Brand", default=True)
    active_product_advance_info = fields.Boolean(string="Product Advance Info", default=True)
    active_product_variant_info = fields.Boolean(string="Product Variant Info", default=True)
    active_product_accessory = fields.Boolean(string="Product Accessory", default=True)
    active_product_alternative = fields.Boolean(string="Product Alternative", default=True)
    active_product_pager = fields.Boolean(string="Product Pager", default=True)
    active_product_sticky = fields.Boolean(string="Product Stocky", default=True)

# class ThemeUtilsExtend(models.AbstractModel):
#     _inherit = 'theme.utils'

#     @api.model
#     def _reset_default_config(self):
#         # Reinitialize some css customizations
#         self.env['web_editor.assets'].make_scss_customization(
#             '/website/static/src/scss/options/user_values.scss',
#             {
#                 'font': 'null',
#                 'headings-font': 'null',
#                 'navbar-font': 'null',
#                 'buttons-font': 'null',
#                 'color-palettes-number': 'null',
#                 'color-palettes-name': 'null',
#                 'btn-ripple': 'null',
#                 'header-template': 'null',
#                 'footer-template': 'null',
#                 'footer-scrolltop': 'null',
#             }
#         )

#         # Reinitialize effets
#         self.disable_asset('website.ripple_effect_scss')
#         self.disable_asset('website.ripple_effect_js')
#         # custom header
#         self.disable_view('website.template_header_hamburger')
#         self.disable_view('website.template_header_vertical')
#         self.disable_view('website.template_header_sidebar')
#         self.disable_view('website.template_header_slogan')
#         self.disable_view('website.template_header_contact')
#         self.disable_view('website.template_header_boxed')
#         self.disable_view('website.template_header_centered_logo')
#         self.disable_view('website.template_header_image')
#         self.disable_view('website.template_header_hamburger_full')
#         self.disable_view('website.template_header_magazine')
#         self.disable_view('website.template_header_default')
#         self.enable_view('atharva_theme_base.atharva_header')

#         # custom footer
#         self.disable_view('website.template_footer_descriptive')
#         self.disable_view('website.template_footer_centered')
#         self.disable_view('website.template_footer_links')
#         self.disable_view('website.template_footer_minimalist')
#         self.disable_view('website.template_footer_contact')
#         self.disable_view('website.template_footer_call_to_action')
#         self.disable_view('website.template_footer_headline')
#         self.disable_view('website.footer_custom')
#         self.enable_view('atharva_theme_base.atharva_footer')
#         # Reinitialize footer scrolltop template
#         self.disable_view('website.option_footer_scrolltop')


class WebsiteMenuTabs(models.Model):
    _name = "as.megamenu.tabs"
    _description = "Website Menu Tabs"

    DEFAULT_DESCRIPTION = '<section class="as_mega_menu as-mega-menu-preview-section" data-as-snippet="as_mega_menu">\
                                <div class="container as-mega-menu-welcome">\
                                    <div class="as-mm-wc-in">\
                                        <button class="btn as-e-btn-primary as-config"><i class="fa fa-pencil-square-o"/> Configure Alan Mega Menu </button>\
                                        <div class="as-mm-wc-img">\
                                            <img src="/atharva_theme_base/static/src/img/snippets/megamenu/configure-mega-menu.svg" />\
                                        </div>\
                                    </div>\
                                </div>\
                            </section>'

    name = fields.Char(required=True)
    icon = fields.Image(max_width=100, max_height=100, required=True)
    redirect = fields.Char(string="Redirect Link", default="/", required=True)
    description = fields.Html(default=DEFAULT_DESCRIPTION, sanitize_attributes=False)

class WebsiteMenuAlanTags(models.Model):
    _inherit = "website.menu"

    is_tag_active = fields.Boolean(string="Menu Tag")
    tag_text_color = fields.Char(string="Tag Text Color")
    tag_bg_color = fields.Char(string="Tag Background Color")
    tag_text = fields.Char(string="Tag Text", translate=True)

    hlt_menu = fields.Boolean(string="Highlight Menu")
    hlt_menu_bg_color = fields.Char(string="Background Color")
    hlt_menu_ft_col = fields.Char(string="Font Color")
    hlt_menu_icon = fields.Char(string="Fav Icon")

    active_mega_tabs = fields.Boolean(string="Active Megamenu Tabs")
    megamenu_tabs = fields.Many2many("as.megamenu.tabs", string="Megamenu Tabs")

    @api.model
    def get_tree(self, website_id, menu_id=None):
        website = self.env['website'].browse(website_id)

        def make_tree(node):
            menu_url = node.page_id.url if node.page_id else node.url
            menu_node = {
                'fields': {
                    'id': node.id,
                    'name': node.name,
                    'url': menu_url,
                    'new_window': node.new_window,
                    'is_mega_menu': node.is_mega_menu,
                    'sequence': node.sequence,
                    'parent_id': node.parent_id.id,
                    'tag_text': node.tag_text,
                    'is_tag_active': node.is_tag_active,
                    'tag_bg_color': node.tag_bg_color,
                    'tag_text_color': node.tag_text_color,
                    'hlt_menu': node.hlt_menu,
                    'hlt_menu_bg_color': node.hlt_menu_bg_color,
                    'hlt_menu_ft_col': node.hlt_menu_ft_col,
                    'hlt_menu_icon':node.hlt_menu_icon,
                },
                'children': [],
                'is_homepage': menu_url == (website.homepage_url or '/'),
            }
            for child in node.child_id:
                menu_node['children'].append(make_tree(child))
            return menu_node
        menu = menu_id and self.browse(menu_id) or website.menu_id
        return make_tree(menu)


class DataForm(models.Model):
    _inherit = 'ir.ui.view'

    def remove_unused_data_frame(self):
        frame_ids = self.env['ir.ui.view'].sudo().search([('arch_db', 'like', 'data-frame-id')]);
        lst=[]
        for object in frame_ids:
            string= object.arch_db
            x = re.findall('(?<=data-frame-id=")(.*?)"', string)
            for data in x:
                lst.append(data)

        return lst

class BlogExtend(models.Model):
    _inherit = "blog.post"

    cover_background = fields.Char(compute="_get_background_image")

    @api.depends('cover_properties')
    def _get_background_image(self):
        for i in self:
            cover_properties = json.loads(i.cover_properties)
            i.cover_background = cover_properties['background-image']
