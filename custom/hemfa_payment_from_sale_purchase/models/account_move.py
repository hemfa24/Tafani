# -*- coding: utf-8 -*-

from odoo import models, fields, api


class accountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        if have register paymetn in sale or purchase then reconcile it
        """
        res = super(accountMove,self).action_post()
        for rec in self:
            if rec.move_type == 'in_invoice':
                purchase = self.env['purchase.order'].search([('invoice_ids','in',[rec.id,])], limit=1)
                if purchase:
                    for payment in purchase.payment_ids:
                        dest_line = payment.move_id.line_ids.filtered(lambda mv: mv.account_id.id == payment.destination_account_id.id)
                    
                        rec.js_assign_outstanding_line(dest_line.id)
                        rec._compute_amount()
            elif rec.move_type == 'out_invoice':
                sale = self.env['sale.order'].search([('invoice_ids','in',[rec.id,])], limit=1)
                if sale:
                    for payment in sale.payment_ids:
                        dest_line = payment.move_id.line_ids.filtered(lambda mv: mv.account_id.id == payment.destination_account_id.id)
                    
                        rec.js_assign_outstanding_line(dest_line.id)
                        rec._compute_amount()

        # 1/0

        return res


