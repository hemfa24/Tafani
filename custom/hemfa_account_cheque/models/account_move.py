# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError



class accountMove(models.Model):
    _inherit = "account.move"

    account_cheque_id = fields.Many2one('account.cheque', 'Journal Item')
    is_move_to_reconcile = fields.Boolean()
    payment_state_cheque = fields.Selection(
            selection=[
                ('not_paid', 'Not Paid'),
                ('in_payment', 'In Payment'),
                ('paid', 'Paid'),
                ('partial', 'Partially Paid'),
                ('reversed', 'Reversed'),
                ('invoicing_legacy', 'Invoicing App Legacy'),
            ],
            string="Payment Status",
            related=False, store=True, readonly=True,
            copy=False,
            tracking=True,
        )
    amount_residual_cheque = fields.Monetary(
        string='Amount Due',
        compute=False, store=True,
    )
    def get_line_state(self):
        for rec in self:
            if rec.line_ids:
                rec.line_ids._get_line_state()


class accountMoveLine(models.Model):
    _inherit = "account.move.line"

    line_state = fields.Selection([('not', 'Not'), ('cashed', 'Cashed'), ], compute="_get_line_state", store=True)

    @api.depends('move_id.account_cheque_id', 'move_id.account_cheque_id.status1', 'move_id.account_cheque_id.status',
                 'payment_id.state', 'move_id.state')
    def _get_line_state(self):
        for rec in self:
            if rec.move_id.state == 'posted' and rec.move_id.account_cheque_id and (
                    rec.move_id.account_cheque_id.status1 == 'cashed' or rec.move_id.account_cheque_id.status == 'cashed'):
                rec.line_state = 'cashed'
            elif rec.payment_id and rec.payment_id.state == 'posted':
                rec.line_state = 'cashed'
            else:
                rec.line_state = 'not'

    def unlink(self):
        for rec in self:
            if rec.move_id.state != 'draft' and not self._context.get('force_delete'):
                raise UserError(("Sorry you can't Delete because Record in State not in Draft"))

        res = super(accountMoveLine, self).unlink()

        return res
