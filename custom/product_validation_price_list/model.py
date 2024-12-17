
from odoo import models, fields, api,_
from odoo.osv import expression
from odoo.exceptions import ValidationError, UserError



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('list_price', 'standard_price')
    @api.onchange('list_price')
    def onchange_list_price(self):
        for recod in self:
            if recod.standard_price > recod.list_price: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price'):
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))

      
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('list_price', 'standard_price')
    @api.onchange('list_price')
    def onchange_list_price(self):
        for recod in self:
            if recod.standard_price > recod.list_price: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price'):
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))


class ProductDynimac(models.Model):
    _inherit = 'product.template.barcode'

    @api.depends('product_id', 'price')
    @api.onchange('price')
    def onchange_list_price(self):
        for recod in self:
            if recod.product_id.standard_price > recod.price and not recod.price_lst: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price') :
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))
    @api.model
    def create(self, vals):
        res = super(ProductDynimac, self).create(vals)
        if res.product_id.standard_price > res.price  and not res.price_lst: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price'):
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))
        return res
class ProductpriceList(models.Model):
    _inherit = 'product.pricelist.item'

    @api.depends('product_id', 'fixed_price')
    @api.onchange('fixed_price')
    def onchange_list_price(self):
        for recod in self:
            if recod.product_id.standard_price > recod.fixed_price: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price'):
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))

    @api.model
    def create(self, vals):
        res = super(ProductpriceList, self).create(vals)
        if res.product_id.standard_price > res.fixed_price: 
                if not self.env.user.has_group('product_validation_price_list.product_less_price'):
                    raise ValidationError(_("You can not edit Sales Price less Cost amount"))
        return res
                    