
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomWarehouseStockRequest(models.Model):
    _inherit = 'custom.warehouse.stock.request'

    @api.onchange('barcode')
    def onchange_barcode_set_product(self):
        for rec in self:
            if rec.barcode:
                product_id = self.env['product.product'].search([('barcode','=',rec.barcode)])
                search_product_code = self.env["product.template.barcode"].sudo().search(
                    [('name', '=', rec.barcode),
                     ('available_item', '=', True)
                     ], limit=1)
                if product_id:
                    lines = rec.warehouse_stock_request_line_ids.filtered(lambda l: l.product_id.id == product_id.id )
                    if lines:
                        for line in lines:
                            line.demand_qty += 1
                    else:
                        line_val = {
                                    # 'inventory_id': rec.id,
                                    'product_id': product_id.id,
                                    'description':product_id.display_name,
                                    'product_uom':product_id.uom_id.id,
                                    'demand_qty': 1,
                                    
                                }

                        rec.warehouse_stock_request_line_ids = [(0, 0, line_val)]
                elif search_product_code:
                    lines = rec.warehouse_stock_request_line_ids.filtered(lambda l: l.product_id.id == search_product_code.product_id.id and l.product_uom.id == search_product_code.unit.id)
                    if lines:
                        for line in lines:
                            line.demand_qty += 1
                    else:
                        line_val = {
                                    # 'inventory_id': rec.id,
                                    'product_id': search_product_code.product_id.id,
                                    'description':search_product_code.product_id.display_name,
                                    'product_uom':search_product_code.unit.id,
                                    'demand_qty': 1,
                                    
                                }

                        rec.warehouse_stock_request_line_ids = [(0, 0, line_val)]
                else:
                    raise UserError(
                        _("Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (rec.barcode))
            rec.barcode = False