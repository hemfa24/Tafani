# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class CrmLead(models.Model):
    _inherit = "crm.lead"

    request_quota_line = fields.One2many('request.quotation', 'lead_id', 'Product Request')

#    @api.multi #odoo13
    def custom_create_quotation(self):
        quot_list = []
        for rec in self:
            if not rec.request_quota_line:
                raise UserError(_("No product lines found."))
            if all(req.custom_order_id for req in rec.request_quota_line):
                raise UserError(_("No product lines found or already created."))
            sale_obj = self.env['sale.order']
            sale_line_obj = self.env['sale.order.line']
            if not rec.partner_id:
                raise UserError(_("Please create customer and link on oppotunity to create quote."))
            sale_dict = {'partner_id':rec.partner_id.id, 'origin':rec.name, 'opportunity_id':rec.id}
            sale_order = sale_obj.create(sale_dict)
            quot_list.append(sale_order.id)
            for request in rec.request_quota_line:
                if not request.custom_order_line_id:
                    lines = {
                        'product_id':request.product_id.id,
                        # 'product_qty':request.product_uom_qty,
                        'product_uom_qty':request.product_uom_qty,
                        'order_id': sale_order.id,
                        'product_uom':request.product_uom.id,
                    }
                    line = sale_line_obj.create(lines)
                    request.write({'custom_order_line_id':line.id})
        # result = self.env.ref('sale.action_orders')
        result = self.env.ref("sale.action_quotations_with_onboarding")
        action_ref = result or False
        result = action_ref.sudo().read()[0]
        result['domain'] = str([('id', 'in', quot_list)])
        return result

class RequestQuotation(models.Model):

    _name = 'request.quotation'
    _description = 'Request Lines CRM'
    _order = 'lead_id, id'

    lead_id = fields.Many2one('crm.lead', string='Opportunity')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    # product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    qty_onhand = fields.Float(string="Quantity on Hand")
    custom_order_line_id = fields.Many2one('sale.order.line',string="Sale Order Line",copy=False,)
    custom_order_id = fields.Many2one('sale.order',string="Sale Order",copy=False,related='custom_order_line_id.order_id')

#    @api.multi #odoo13
    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.id
            if rec.product_id:
                rr = rec.product_id._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False)
                rec.qty_onhand = rr[rec.product_id.id]['qty_available']


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
