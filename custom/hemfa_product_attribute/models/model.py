from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, ValidationError ,UserError   
from random import randint

class SaleLineInhertValueIds(models.Model):
    _inherit = 'sale.order.line'    
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value',related="product_id.product_template_variant_value_ids", string="Variant Values")
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
    
class PurchaseLineInhertValueIds(models.Model):
    _inherit = 'purchase.order.line'    
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value',related="product_id.product_template_variant_value_ids", string="Variant Values")
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")

class StockLineInhertValueIds(models.Model):
    _inherit = 'custom.warehouse.stock.request.line'    
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value',related="product_id.product_template_variant_value_ids", string="Variant Values")
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
class PriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
class StockMove(models.Model):
    _inherit = "stock.move"
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
class InventoryLineTemplates(models.Model):
    _inherit = "inventory.adjustment.template.new.line"
    product_attribute= fields.Many2many(related="product_id_new.product_template_attribute_value_ids", string="product attribute")
class StockQuant(models.Model):
    _inherit = "stock.quant"
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    product_attribute= fields.Many2many(related="product_id.product_template_attribute_value_ids", string="product attribute")
class AccountMove(models.Model):
    _inherit = "account.move"
    invoice_date = fields.Date(
        string='Invoice/Bill Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
        copy=False,
        default=fields.Date.context_today
    )
class ProductAttributeInherit(models.Model):
    _inherit = "product.attribute"


    def write(self, vals):
        """Override to make sure attribute type can't be changed if it's used on
        a product template.

        This is important to prevent because changing the type would make
        existing combinations invalid without recomputing them, and recomputing
        them might take too long and we don't want to change products without
        the user knowing about it."""
        save_vale =0
        if 'create_variant' in vals:
            save_vale =vals.get('create_variant')
            for rec in self:
                rec.number_related_products=0

        res = super(ProductAttributeInherit, self).write(vals)
        return res