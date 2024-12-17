# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentSalePurchcase(models.TransientModel):
    _name = 'account.payment.sale_purchase'
    _description = 'Register Payment Sale Purchase'

    # == Business fields ==
    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        )
    communication = fields.Char(string="Memo", store=True, readonly=False,
        )
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        
        help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    

    # == Fields given through the context ==
    # line_ids = fields.Many2many('account.move.line', 'account_payment_register_move_line_rel', 'wizard_id', 'line_id',
    #     string="Journal items", readonly=True, copy=False,)
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', store=True, copy=False,
        )
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], store=True, copy=False,
        )
    company_id = fields.Many2one('res.company', store=True, copy=False,
        )
    company_currency_id = fields.Many2one('res.currency', string="Company Currency",
        related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner',
        string="Customer/Vendor", store=True, copy=False, ondelete='restrict',
        )

    # == Payment methods fields ==
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method',
        readonly=False, store=True,
        compute='_compute_payment_method_id',
        domain="[('id', 'in', available_payment_method_ids)]",
    )
    available_payment_method_ids = fields.Many2many('account.payment.method',
        compute='_compute_payment_method_fields')    
    hide_payment_method = fields.Boolean(
        compute='_compute_payment_method_fields',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")

    purchase_id = fields.Many2one('purchase.order')
    sale_id = fields.Many2one('sale.order')
    register_amount_limit = fields.Float()

    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def _compute_payment_method_fields(self):
        for wizard in self:
            if wizard.payment_type == 'inbound':
                wizard.available_payment_method_ids = wizard.journal_id.inbound_payment_method_ids
            else:
                wizard.available_payment_method_ids = wizard.journal_id.outbound_payment_method_ids

            wizard.hide_payment_method = len(wizard.available_payment_method_ids) == 1 and wizard.available_payment_method_ids.code == 'manual'

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------
    @api.onchange('journal_id')
    def onchange_journal_select_payment_method(self):
        for rec in self:
            if rec.journal_id and (rec.journal_id.outbound_payment_method_ids or rec.journal_id.inbound_payment_method_ids):
                if rec.payment_type == 'outbound' and rec.journal_id.outbound_payment_method_ids:
                    rec.payment_method_id = rec.journal_id.outbound_payment_method_ids[0].id
                elif rec.payment_type == 'inbound' and rec.journal_id.inbound_payment_method_ids:
                    rec.payment_method_id = rec.journal_id.inbound_payment_method_ids[0].id
            else:
                rec.payment_method_id = False
    def action_create_payments(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_("Amount Must be Greater Than Zero"))
            if rec.amount > rec.register_amount_limit:
                raise UserError(_("Sorry!!, you can't set payment amount more than order amount with all payments, current limit amount is %s ")% rec.register_amount_limit)
            payment_vals = rec._create_payment_vals_from_wizard()
            payment_id = self.env['account.payment'].create(payment_vals)
            payment_id.action_post()

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'payment_method_id': self.payment_method_id.id,
            
        }
        if self.purchase_id:
            payment_vals['purchase_order_id'] = self.purchase_id.id
        elif self.sale_id:
            payment_vals['sale_id'] = self.sale_id.id


        return payment_vals
