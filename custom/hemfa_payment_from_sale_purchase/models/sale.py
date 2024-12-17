# -*- coding: utf-8 -*-

from odoo import models, fields, api
    
class saleOrder(models.Model):
    _inherit = 'sale.order'

    payment_ids = fields.One2many('account.payment','sale_id')
    
    register_amount_limit = fields.Float(compute="_get_register_amount_limit",store=True)
    partner_is_sale_order_payment = fields.Boolean(related="partner_id.is_sale_order_payment")

    is_have_invoice = fields.Boolean(compute="_get_is_have_invoice",store=True)


    @api.depends('order_line.invoice_lines')
    def _get_is_have_invoice(self):
        for rec in self:
            rec.is_have_invoice = False
            if rec.invoice_count > 0:
                rec.is_have_invoice = True

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        res = super(saleOrder,self)._get_invoiced()
        for rec in self:
            rec._get_is_have_invoice()
        return res
        

    @api.depends('amount_total','state','payment_ids','invoice_ids')
    def _get_register_amount_limit(self):
        for rec in self:
            rec.register_amount_limit = 0

            limit = rec.amount_total
            if rec.payment_ids:
                for payment in rec.payment_ids:
                    if payment.state != 'draft':
                        limit = limit - payment.amount
            rec.register_amount_limit = limit