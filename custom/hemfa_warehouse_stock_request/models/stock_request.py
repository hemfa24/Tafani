from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, ValidationError ,UserError


class StockRequestInherit(models.Model):
    _inherit = 'custom.warehouse.stock.request'

    @api.onchange('stock_request_type')
    def _onchange_stock_request_type(self):
        for record in self :
            if record.stock_request_type:
                if record.stock_request_type =='employee_request':
                    record.picking_type_id=False
                    return {'domain':
                    {
                        'picking_type_id': [('code', 'in', ['outgoing','internal'])],
                        'sec_picking_type_id': [('code', 'in', ['outgoing','internal'])],

                        }
                    }
                else:
                    return {'domain': {'picking_type_id': []}}
    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for record in self :
            record.location_id =record.picking_type_id.default_location_src_id or False
    @api.onchange('sec_picking_type_id')
    def _onchange_sec_picking_type_id(self):
        for record in self :
            record.location_dest_id =record.sec_picking_type_id.default_location_dest_id or False