# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class accountPayment(models.Model):
    _inherit = 'account.payment'

    purchase_order_id = fields.Many2one('purchase.order')
    partner_is_purchase_order_payment = fields.Boolean(related="partner_id.is_purchase_order_payment")
    sale_id = fields.Many2one('sale.order')
    partner_is_sale_order_payment = fields.Boolean(related="partner_id.is_sale_order_payment")

    pay_sale = fields.Boolean()
    pay_purchase = fields.Boolean()
    def action_post(self):
        res = super(accountPayment,self).action_post()
        for rec in self:
            if rec.pay_sale and rec.sale_id:
                rec.sale_id._get_register_amount_limit()
            if rec.pay_purchase and rec.purchase_order_id:
                rec.purchase_order_id._get_register_amount_limit()
        return res

    def action_draft(self):
        res = super(accountPayment,self).action_draft()
        for rec in self:
            if rec.pay_sale and rec.sale_id:
                rec.sale_id._get_register_amount_limit()
            if rec.pay_purchase and rec.purchase_order_id:
                rec.purchase_order_id._get_register_amount_limit()
        return res
    #hide register_amount_limit
    @api.constrains('pay_sale','pay_purchase','sale_id','purchase_order_id')
    def check_sale_purchase_limit(self):
        for rec in self:
            if rec.pay_sale and rec.sale_id and rec.amount > rec.sale_id.register_amount_limit:
                raise UserError(_("Sorry you can't pay for sale order more than "+str(rec.sale_id.register_amount_limit)))
            if rec.pay_purchase and rec.purchase_order_id and rec.amount > rec.purchase_order_id.register_amount_limit:
                raise UserError(_("Sorry you can't pay for purchase order more than "+str(rec.purchase_order_id.register_amount_limit)))

            
    @api.onchange('sale_id','purchase_order_id')
    def onchange_sale_purchase_set_amount(self):
        for rec in self:
            if rec.sale_id:
                rec.amount = rec.sale_id.register_amount_limit
            if rec.purchase_order_id:
                rec.amount = abs(rec.purchase_order_id.register_amount_limit)

    
    @api.onchange('partner_id','payment_type')
    def onchange_set_purchase_sale(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.payment_type == 'inbound':
                    rec.pay_purchase = False
                    rec.purchase_order_id = False
                if rec.payment_type == 'outbound':
                    rec.pay_sale = False
                    rec.sale_id = False
                if rec.is_internal_transfer:
                    rec.pay_purchase = rec.purchase_order_id = rec.pay_sale = rec.sale_id  = False
                if not rec.pay_purchase:
                    rec.purchase_order_id = False
                if not rec.pay_sale:
                    rec.sale_id = False
                    
