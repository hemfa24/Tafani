# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EditUnitPrice(models.TransientModel):
    _name = 'edit.lines.price.unit'

    res_model = fields.Char(
        string='Model'
    )
    res_id = fields.Char(
        string='Id'
    )
    price_unit = fields.Float(
        string='Price Unit'
    )

    @api.model
    def default_get(self, field_list):
        res = super(EditUnitPrice, self).default_get(field_list)
        if self._context.get('active_model') and self._context.get('active_id'):
            res.update({
                'res_model': self._context.get('active_model'),
                'res_id': self._context.get('active_id'),
            })
        return res

    def update_unit_price(self):
        if self.res_model and self.res_id:
            res_obj_id = self.env[self.res_model].browse(int(self.res_id))
            if self.price_unit > 0.0:
                res_obj_id.price_unit = self.price_unit
                res_obj_id.discount_amount = 0.0
                res_obj_id.unit_price_before_discount = self.price_unit
            else:
                ValidationError(_("Price Unit shouldn't be 0."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
