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

class InventoryAdujustmentsTemplates(models.Model):
    _name = 'inventory.adjustment.template.new'

    name = fields.Char('Name',readonly=False)
    location_id = fields.Many2one('stock.location', 'Inventoried Location', readonly=False)
    adjst_line_ids = fields.One2many('inventory.adjustment.template.new.line', 'inventory_id', string='Adjustments Lines',readonly=False)
    parent_inventory_id = fields.Many2one('stock.quant', string='Inventory ID')
    barcode = fields.Char()
    
    @api.onchange('barcode')
    def onchange_barcode_set_product(self):
        for rec in self:
            if rec.barcode:
                product_id = self.env['product.product'].search([('barcode','=',rec.barcode)])
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
                else:
                    raise UserError(
                        _("Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (rec.barcode))
            rec.barcode = False
    def action_apply_counted_to_real(self):
        for rec in self:
            for line in rec.adjst_line_ids:
                line.product_qty = line.counted_qty


    def action_view_related_move_lines(self):
        self.ensure_one()
        domain = [('inventory_id', '=', self.id)]
        action = {
            'name': _('Product'),
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.adjustment.template.new.line',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
            'context':{'default_location_id_new':self.location_id.id,'default_inventory_id':self.id}
        }
        return action

class InventoryLineTemplates(models.Model):
    _name = "inventory.adjustment.template.new.line"
    _description = "Adjustments Lines"

    inventory_id = fields.Many2one(
        'inventory.adjustment.template.new', 'Inventory',
        index=True, ondelete='cascade')
    product_id_new = fields.Many2one(
        'product.product', 'Product')
    location_id_new = fields.Many2one(related='inventory_id.location_id', string='Location',store=True, readonly=True)
    product_qty = fields.Float(
        'Real Quantity', default=0)
    counted_qty = fields.Float(
        'Counted Quantity', default=0) 
    barcode = fields.Char(related="product_id_new.barcode",store=1)
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value',related="product_id_new.product_template_variant_value_ids", string="Variant Values")
    

    def action_reset(self):
        for rec in self:
            rec.product_qty = 0
        
        
class StockInventoryTemplate(models.Model):
    _inherit='stock.quant'

    inventory_template = fields.Many2one('inventory.adjustment.template.new',string="Template")

    def action_start(self):
        list = []
        if self.inventory_template:
            for line in self.inventory_template.adjst_line_ids:
                val={}
                val['product_id'] = line.product_id_new.id
                val['location_id'] = line.location_id_new.id
                val['product_qty'] = line.product_qty
                list.append((0,0,val))
        self.write({'line_ids':list})

        res = super(StockInventoryTemplate,self).action_start()
        return res

    def save_template(self):
        # template_id = self.env['inventory.adjustment.template.new']
        inventory_id = self.env['inventory.adjustment.template.new'].search([('parent_inventory_id','=',self.id)])
        if not inventory_id:
            for location in self.location_ids:
                list_2 = []
                for line in self.line_ids:
                    val = {}
                    val['product_id_new'] = line.product_id.id
                    val['product_qty'] = line.product_qty
                    list_2.append((0, 0, val))
                # template_id.write({'adjst_line_ids': list_2})

                vals = {
                    'name': self.name,
                    'location_id':location.id,
                    'parent_inventory_id':self.id,
                    'adjst_line_ids': list_2,
                }
                inventory_id = self.env['inventory.adjustment.template.new'].create(vals)

                return {
                    'res_model': 'inventory.adjustment.template.new',
                    'type': 'ir.actions.act_window',
                    'res_id': inventory_id.id,
                    'context': {},
                    'view_mode': 'form',
                    'view_id': self.env.ref("inventory_adjustment_template.view_inventory_adjustments_temp_form").id,
                }
        else:
            return {
                'res_model': 'inventory.adjustment.template.new',
                'type': 'ir.actions.act_window',
                'res_id': inventory_id.id,
                'context': {},
                'view_mode': 'form',
                'view_id': self.env.ref("inventory_adjustment_template.view_inventory_adjustments_temp_form").id,
            }


