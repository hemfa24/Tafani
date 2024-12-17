from email.policy import default
from itertools import product
import logging
from datetime import timedelta
from functools import partial
from odoo.exceptions import UserError, ValidationError
from bisect import bisect_left
from collections import defaultdict
import re

import psycopg2
from odoo.osv import expression
from odoo.osv.expression import OR

from odoo import api, fields, models, tools, _
from odoo.tools import barcode, float_is_zero
from odoo.http import request

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = 'res.company'

    product_setting = fields.Boolean(
        'Product Setting', default=False, store=True)


class pos_multi_barcode_opt(models.Model):
    _name = 'pos.multi.barcode.options'

    name = fields.Char('Barcode', required=True, unique=True, copy=False)
    qty = fields.Float("Quantity")
    price = fields.Float("Price")
    unit = fields.Many2one("uom.uom", string="Unit")
    price_lst = fields.Many2one('product.pricelist')
    product_id = fields.Many2one("product.product", string="Product")
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", store=True, related='product_id.product_tmpl_id')
    product_name = fields.Char(
        string="Product Name", store=True, related='product_id.product_tmpl_id.name')

    @api.model
    def get_data_for_pos(self):
        data = self.sudo().search([])
        return data

    @api.depends('product_tmpl_id')
    def _get_product(self):
        for rec in self:
            if rec.product_tmpl_id and not rec.product_id:
                product_id = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_tmpl_id.id)],
                                                                limit=1)
                if product_id:
                    rec.product_id = product_id.id

    @api.onchange('unit')
    def unit_id_change(self):
        domain = {
            'unit': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        return {'domain': domain}

    @api.constrains('name')
    def _barcode_const(self):
        for record in self:
            if record.name:
                barcode_stander = self.env['product.product'].search(
                    [('barcode', '=', record.name)])
                if barcode_stander:
                    raise UserError(
                        _("Standard Barcode %s has been duplicated." % record.name))
                if not record.qty or not record.price or not record.unit:
                    raise UserError(_("Qty,Price and UOM are Mandatory."))
                other_record = self.env['pos.multi.barcode.options'].sudo().search(
                    [('id', '!=', record.id or record._origin.id), ('name', '=', record.name)])
                if other_record:
                    raise UserError(
                        _("Options Barcode %s has been duplicated." % record.name))

#############################################################################################################
#############################################################################################################


class product_product(models.Model):
    _inherit = 'product.product'

    ls_company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id
    )

    pos_multi_barcode_option = fields.One2many(
        'pos.multi.barcode.options', 'product_id', string='Barcodes')
    ls_active = fields.Boolean(
        related='ls_company_id.product_setting', store=True)


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    barcode_custom = fields.Char('Barcode')

    @api.onchange('barcode_custom')
    def onchange_barcode_custom(self):
        obj = self.env['pos.multi.barcode.options'].sudo().search([
            ('name', '=', self.barcode_custom)
        ], limit=1)
        if obj:
            self.product_id = obj.product_id
            self.write({'price_unit': obj.price})
            self.product_uom_qty = obj.qty
