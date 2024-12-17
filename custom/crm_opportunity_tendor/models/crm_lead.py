# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import fields, models, api, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    requisition_ids = fields.One2many(
        'purchase.requisition', 
        'custom_lead_id', 
        string='Requisition',
        readonly=True,
        copy=False,
    )
    purchase_requisition_count = fields.Integer(
        string='Purchase Requisitions',
        compute='compute_purchase_requisition_count',
        store=True,
        copy=False,
    )

    # @api.multi
    @api.depends('requisition_ids')
    def compute_purchase_requisition_count(self):
        for purchase in self:
            purchase_requisition_count = len(purchase.requisition_ids)
            purchase.purchase_requisition_count = purchase_requisition_count

    # @api.multi
    def create_purchase_tender(self):
        for rec in self:
            purchase_req = self.env['purchase.requisition']
            purchase_req_line = self.env['purchase.requisition.line']
            supplier_dict= {}
            
            for request in rec.request_rfq_line:
                if request.partner_id:
                    if request.partner_id not in supplier_dict:
                        supplier_dict[request.partner_id] = [request]
                    else:
                        supplier_dict[request.partner_id].append(request)
                else:
                    raise Warning("Please set Supplier")

            prq_list = []
            for supp in supplier_dict:
                purchase_req_dict = {'vendor_id':supp.id,'custom_lead_id':rec.id,'origin':rec.name,'ordering_date': datetime.today()}
                purchase_req_order = purchase_req.create(purchase_req_dict)
                prq_list.append(purchase_req_order.id)
                for request in supplier_dict[supp]:
                    lines = {
                        'product_id': request.product_id.id,
                        'product_qty': request.product_uom_qty,
                        'product_uom_id': request.product_uom.id,
                        'price_unit': request.product_id.standard_price,
                        'schedule_date': fields.date.today(),
                        'requisition_id': purchase_req_order.id,
                    }
                    purchase_req_line.create(lines)
        result = self.env.ref('purchase_requisition.action_purchase_requisition')
        action_ref = result or False
        result = action_ref.sudo().read()[0]
        result['domain'] = str([('id', 'in', prq_list)])
        return result

    # @api.multi
    def open_purchase_tender(self):
        for rec in self:
            self.env.cr.execute("select DISTINCT ce.id FROM purchase_requisition ce WHERE (ce.custom_lead_id = %s)", (rec.id,))
            res = self.env.cr.fetchall()
            prq_list = []
            for purchase in res:
                prq_list += purchase
            result = self.env.ref('purchase_requisition.action_purchase_requisition')
            action_ref = result or False
            result = action_ref.sudo().read()[0]
            result['domain'] = str([('id', 'in', prq_list)])
            return result