# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError ,UserError



class InventoryLineTemplatesNew(models.Model):
    _inherit = "inventory.adjustment.template.new.line"
    product_uom= fields.Many2one(related="product_id_new.uom_id", string="Unit of Measure" ,store=True)
class InventoryAdujustmentsTemplates(models.Model):
    _inherit = 'inventory.adjustment.template.new'

    
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
                    lines = rec.adjst_line_ids.filtered(lambda l: l.product_id_new.id == product_id.id)
                    if lines:
                        for line in lines:
                            line.counted_qty += 1
                    else:
                        line_val = {
                                    # 'inventory_id': rec.id,
                                    'product_id_new': product_id.id,
                                    'location_id_new': rec.location_id.id,
                                    'counted_qty': 1,
                                    
                                }

                        rec.adjst_line_ids = [(0, 0, line_val)]
                elif search_product_code:
                    lines = rec.adjst_line_ids.filtered(lambda l: l.product_id_new.id == search_product_code.product_id.id and l.product_uom.id == search_product_code.unit.id)
                    if lines:
                        for line in lines:
                            line.counted_qty += 1
                    else:
                        line_val = {
                                    # 'inventory_id': rec.id,
                                    'product_id_new': search_product_code.product_id.id,
                                    'location_id_new': rec.location_id.id,
                                    'counted_qty': 1,
                                    'product_uom' :search_product_code.unit.id,
                                    
                                }

                        rec.adjst_line_ids = [(0, 0, line_val)]
                else:
                    raise UserError(
                        _("Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (rec.barcode))
            rec.barcode = False