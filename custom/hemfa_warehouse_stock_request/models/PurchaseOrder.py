from odoo import api, fields, models, _
from odoo.exceptions import UserError

class purchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    # notification_to_user_id = fields.Many2one('res.users',string="Notification To")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_request_id = fields.Many2one(
        'custom.warehouse.stock.request',
        string='Purchase request',
        domain="[('stock_request_type', '=', 'purchase_request'), ('is_purchased', '=', False), ('state', '=', 'confirmed')]")

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()

        for rec in self:
            if rec.purchase_request_id:
                rec.purchase_request_id.is_purchased = True


        return res
    
    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()

        for rec in self:
            if rec.purchase_request_id:
                rec.purchase_request_id.is_purchased = False


        return res
    # @api.model
    # def create(self,vals):
        
    #     res = super(PurchaseOrder, self).create(vals)

    #     for rec in res:
    #         if rec.requisition_id and rec.requisition_id.notification_to_user_id:
    #             self.env['mail.activity'].create({
    #                 'display_name': 'text',
    #                 'summary': 'text',
    #                 'date_deadline': rec.requisition_id.date_end,
    #                 'user_id': rec.requisition_id.notification_to_user_id.id,
    #                 'res_id': rec.requisition_id.id,
    #                 'res_model_id': self.env['ir.model'].search([('model','=','purchase.requisition')],limit=1).id,
    #                 'activity_type_id': 4
    #                 })


    #     return res

    @api.onchange('purchase_request_id')
    def onchange_purchase_request_id(self):
        self.partner_id = self.purchase_request_id.partner_id
        self.order_line = [[5, 0, 0]]
        for line in self.purchase_request_id.warehouse_stock_request_line_ids:
            
            self.order_line = [[0, 0, {"product_id": line.product_id.id, "name": line.description,
                                       "product_qty": line.demand_qty, "product_uom": line.product_uom.id, }]]