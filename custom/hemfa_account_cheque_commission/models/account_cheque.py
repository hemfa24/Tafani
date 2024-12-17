# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    commission_ids = fields.One2many(
        'sale.commission.lines',
        'cheque_id',
        string='Sales Commissions',
        help="Sale Commission related to this invoice(based on sales person)"
    )
    is_invoice_checked_with_commission = fields.Boolean(
        'Checked Invoice with commission',
        compute='_compute_invoice_checked_wth_comm',
        store=True
    )

    @api.depends('invoice_ids', 'invoice_ids.check')
    def _compute_invoice_checked_wth_comm(self):
        for rec in self:
            if any(move.check for move in rec.invoice_ids):
                rec.is_invoice_checked_with_commission = True
            else:
                rec.is_invoice_checked_with_commission = False

    # def action_incoming_cashed(self):
    #     res = super(AccountCheque, self).action_incoming_cashed()
    #     print ("!!!!!!!!!!!!!!!!!action_incoming_cashed")
    #     commission_configuration = self.env.user.company_id.commission_configuration
    #     print ("~~~~~~~~~~~~~~~~~~~~~~~~~~",commission_configuration)
    #     if commission_configuration == 'payment':
    #         self.get_treasury_payment_commission()
    #     return res

    def get_treasury_payment_commission(self, outstanging_inv_ids=None):
        for cheque in self:
            invoice_commission_ids = []
            invoice_ids = outstanging_inv_ids or cheque.invoice_ids.filtered(lambda inv: inv.check)
            for invoice in invoice_ids.with_context(default_partner_type=False):
                if invoice.amount_residual != 0.0:
                    continue
                commission_obj = self.env['sale.commission']
                commission_id = self.env['sale.commission']
                if invoice.sale_commission_id:
                    commission_id = invoice.sale_commission_id

                    if invoice.sale_commission_id.compute_for == 'sales_person':
                        if invoice.user_id not in invoice.sale_commission_id.user_ids:
                            return False

                    if invoice.sale_commission_id.compute_for == 'sales_team':
                        if invoice.team_id not in invoice.sale_commission_id.sales_team:
                            return False

                    if invoice.sale_commission_id.compute_for == 'agents' and not invoice.agents_ids:
                        return False

                if not commission_id:
                    return False

                if commission_id.comm_type == 'categ':
                    invoice_commission_ids = invoice.get_categ_commission(commission_id, invoice)
                elif commission_id.comm_type == 'partner':
                    invoice_commission_ids = invoice.get_partner_commission(commission_id, invoice)
                elif commission_id.comm_type == 'product':
                    invoice_commission_ids = invoice.get_categ_commission(commission_id, invoice)
                else:
                    invoice_commission_ids = invoice.get_standard_commission(commission_id, invoice)
                for inv_comm_id in invoice_commission_ids:
                    inv_comm_id.write({
                        'cheque_id': cheque.id
                    })
        return invoice_commission_ids

    def set_to_cancel(self):
        if any(commision.invoiced for commision in self.commission_ids):
            raise ValidationError(
                _("Sorry, The Cheque's commission is already billed you are not allowed to cancel/reset this Cheque."))
        self.commission_ids.unlink()
        res = super(AccountCheque, self).set_to_cancel()
        return res
