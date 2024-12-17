# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class ResCompanyProduct(models.Model):
    _name = 'res.company.product'
    _description = 'model to store previous data company wise'

    product_id = fields.Many2one("product.product", string="Product")
    company_id = fields.Many2one('res.company', required=True,
                                 default=lambda self: self.env.company)
    minimum_qty = fields.Float("Minimum Quantity")
