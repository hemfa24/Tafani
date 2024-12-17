# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
class accountAccount(models.Model):
    _inherit = 'account.account'

    show_in_partner_payable = fields.Boolean()
    show_in_partner_receivable = fields.Boolean()

class accountMove(models.Model):
    _inherit = 'account.move'

    openning_balance_move = fields.Boolean('Openning Balance')
    save_reconcile = fields.Boolean()

    def button_draft(self):
        res = super(accountMove, self).button_draft()
        for move in self:
            if move in move.line_ids.mapped('full_reconcile_id.exchange_move_id'):
                raise UserError(_('You cannot reset to draft an exchange difference journal entry.'))
            if move.tax_cash_basis_rec_id or move.tax_cash_basis_origin_move_id:
                # If the reconciliation was undone, move.tax_cash_basis_rec_id will be empty;
                # but we still don't want to allow setting the caba entry to draft
                # (it'll have been reversed automatically, so no manual intervention is required),
                # so we also check tax_cash_basis_origin_move_id, which stays unchanged
                # (we need both, as tax_cash_basis_origin_move_id did not exist in older versions).
                raise UserError(_('You cannot reset to draft a tax cash basis journal entry.'))
            if move.restrict_mode_hash_table and move.state == 'posted':
                raise UserError(_('You cannot modify a posted entry of this journal because it is in strict mode.'))
            # We remove all the analytics entries for this journal
            move.mapped('line_ids.analytic_line_ids').unlink()
        for rec in self:
            if not rec.save_reconcile:
                rec.mapped('line_ids').remove_move_reconcile()
        self.write({'state': 'draft', 'is_move_sent': False})
        return res


class resPartner(models.Model):
    _inherit = 'res.partner'


    receivable_openning_balance = fields.Float(default=0)

    payable_openning_balance = fields.Float(default=0)

    total_invoiced_with_op = fields.Float(compute = "_invoice_total", string="Total Invoiced With OP",)
    total_bill_with_op = fields.Float(compute = "_invoice_total", string="Total Bill With OP",)
    
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable",
        domain="['|',('show_in_partner_payable','=',True),('account_type', '=', 'liability_payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable",
        domain="['|',('show_in_partner_receivable','=',True),('account_type', '=', 'asset_receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    total_bill = fields.Monetary(compute='_bill_total', string="Total Bills",
        groups='account.group_account_invoice,account.group_account_readonly')
    

    def _invoice_total(self):
        res = super(resPartner,self)._invoice_total()

        for rec in self:
            rec.total_invoiced_with_op = rec.total_bill_with_op = 0

            rec.total_invoiced_with_op = rec.total_invoiced + rec.receivable_openning_balance
            rec.total_bill_with_op = rec.total_bill + rec.payable_openning_balance


        return res


    def get_op_balance(self):
        account_move = self.env['account.move']
        for rec in self:
            moves = account_move.search([('state','=','posted'),('openning_balance_move','=',True)])

            receivable_total = 0 

            payable_total = 0

            for move in moves:
                
                receivable_total = receivable_total + sum([mv_line.debit       for mv_line in move.line_ids.filtered(lambda line: line.partner_id.id == rec.id and line.debit > 0)] )
                payable_total = payable_total + sum([mv_line.credit       for mv_line in move.line_ids.filtered(lambda line: line.partner_id.id == rec.id and line.credit > 0)] )

                
            rec.receivable_openning_balance = receivable_total
            rec.payable_openning_balance = payable_total


    
    def _bill_total(self):
        self.total_bill = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('in_invoice', 'in_refund')),
        ]
        price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_bill = abs(sum(price['price_subtotal'] for price in price_totals if price['partner_id'][0] in child_ids))
