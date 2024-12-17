# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime

from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
# from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    lead_id = fields.Many2one('crm.lead', string=' CRM Opportunity')


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # @api.multi
    def _purchase_order_count(self):
        PurchaseOrder = self.env['purchase.order']
        for sale in self:
            sale.purchase_order_count = PurchaseOrder.search_count([('lead_id', '=', sale.id)])

    purchase_order_count = fields.Integer(compute='_purchase_order_count', string='of RFQ(s)')
    request_rfq_line = fields.One2many('request.rfq', 'lead_id', 'Product Request')
    purchase_order_ids = fields.One2many('purchase.order', 'lead_id', 'Purchase Order')

    # @api.multi
    def open_rfq(self):
        for rec in self:
            self.env.cr.execute("select DISTINCT ce.id FROM purchase_order ce WHERE (ce.lead_id = %s)", (rec.id,))
            res = self.env.cr.fetchall()
            rfq_list = []
            for purchase in res:
                rfq_list += purchase
            result = self.env.ref('purchase.purchase_rfq')
            action_ref = result or False
            result = action_ref.sudo().read()[0]
            result['domain'] = str([('id', 'in', rfq_list)])
            return result
    
    
    # @api.multi
    def create_rfq(self):
        for rec in self:
            purchase_obj = self.env['purchase.order']
            purchase_line_obj = self.env['purchase.order.line']
            supplier_dict= {}
            if not rec.request_rfq_line:
                raise UserError(_("No product lines found."))
            if all(req.custom_purchase_id for req in rec.request_rfq_line):
                raise UserError(_("No product lines found or already created."))

            for request in rec.request_rfq_line:
                if request.custom_purchase_id:
                    continue
                if request.partner_id:
                    if request.partner_id not in supplier_dict:
                        supplier_dict[request.partner_id] = [request]
                    else:
                        supplier_dict[request.partner_id].append(request)
                else:
                    # raise Warning("Please set Supplier")
                    raise UserError(_("Please set Supplier"))

            rfq_list = []
            for supp in supplier_dict:
                purchase_dict = {'partner_id':supp.id, 'origin':rec.name, 'lead_id': rec.id}
                purchase_order = purchase_obj.create(purchase_dict)
                rfq_list.append(purchase_order.id)
                for request in supplier_dict[supp]:
                    if not request.custom_purchase_line_id:
                        lines = {
                            'product_id':request.product_id.id,
                            'product_qty':request.product_uom_qty,
                            'product_uom':request.product_uom.id,
                            'price_unit':request.product_id.standard_price,
                            'name':request.product_id.name,
                            'date_planned': datetime.today(),
                            'order_id': purchase_order.id,
                        }
                        line = purchase_line_obj.create(lines)
                        request.write({'custom_purchase_line_id':line.id})

        result = self.env.ref('purchase.purchase_rfq')
        action_ref = result or False
        result = action_ref.sudo().read()[0]
        result['domain'] = str([('id', 'in', rfq_list)])
        return result


class RequestRFQ(models.Model):

    _name = 'request.rfq'
    _description = 'RFQ Line'
    _order = 'lead_id, id'

    lead_id = fields.Many2one('crm.lead', string='Opportunity')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    # product_uom_qty = fields.Float(string='Request Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom_qty = fields.Float(string='Request Quantity', digits='Product Unit of Measure', required=True, default=1.0) #odoo13 26/02/2020
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    qty_onhand = fields.Float(string="Quantity on Hand")
    custom_purchase_line_id = fields.Many2one('purchase.order.line',string="Purchase Order Line",copy=False,)
    custom_purchase_id = fields.Many2one('purchase.order',string="Purchase Order",copy=False,related='custom_purchase_line_id.order_id')

    # @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.id
            if rec.product_id:
                # rr = rec.product_id._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False)
                rr = rec.product_id._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False, from_date=False, to_date=False) #odoo13 26/02/2020
                rec.qty_onhand = rr[rec.product_id.id]['qty_available']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
