# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError


class ShProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_category_id = fields.Many2one(
        "uom.category",
        "UOM Category",
        related="uom_id.category_id"
    )


class ShBarcodeProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        res = super(ShBarcodeProduct, self)._name_search(name=name, args=args,
                                                         operator=operator, limit=limit, name_get_uid=name_get_uid)
        mutli_barcode_search = list(self._search(
            [('barcode_line_ids', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid))
        print(res)
        if mutli_barcode_search:
            return res + mutli_barcode_search
        return res


