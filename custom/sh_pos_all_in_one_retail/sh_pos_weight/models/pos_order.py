# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.


from odoo import models, fields, api

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_weight = fields.Float(string='Weight (kg)')
    product_volume = fields.Float(string='Volume (m³)')
    total_product_weight = fields.Float(string='Total Weight (kg)',default=0.0)
    total_product_volume = fields.Float(string="Total Volume (m³)",default=0.0)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    enable_product_weight = fields.Boolean(related='config_id.enable_weight')
    enable_product_volume = fields.Boolean(related='config_id.enable_volume')
    total_product_weight = fields.Float(string='Total Weight (kg)', default=0.0)
    total_product_volume = fields.Float(string='Total Volume (m³)', default=0.0)

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        if ui_order.get('total_product_weight', 0.0):
            if ui_order.get('total_product_weight', 0.0) == 'Nan':
                total_product_weight = 0.0
            else:
                try:
                    total_product_weight = float(ui_order.get('total_product_weight', 0.0))
                except:
                    total_product_weight = 0.0
        else:
            total_product_weight = 0.0

        if ui_order.get('total_product_volume', 0.0):
            if ui_order.get('total_product_volume', 0.0) == 'Nan':
                total_product_volume = 0.0
            else:
                try:
                    total_product_volume = float(ui_order.get('total_product_volume', 0.0))
                except:
                    total_product_volume = 0.0
        else:
            total_product_volume = 0.0

        res['total_product_weight'] = total_product_weight
        res['total_product_volume'] = total_product_volume

        return res
