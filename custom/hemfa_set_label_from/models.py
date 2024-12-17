# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _




class AccountAccountType(models.Model):
    _inherit = "account.move.line"

    ref_exist = fields.Boolean(string="ref", compute='_compute_ref_val')
    name = fields.Char(store=True)#related="move_id.ref"

   # @api.depends('move_id', 'move_id.ref')
    def _compute_ref_val(self):
        for rec in self:
            if rec.move_id and rec.move_id.ref:
                rec.ref_exist=True
                rec.name = rec.move_id.ref
            else:
                rec.ref_exist = False
                #rec.write({'name': ''})

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def write(self, vals):
        result = super(AccountPayment, self).write(vals)
        if 'ref' in vals:
            for rec in self:
                for line in rec.move_id.line_ids:
                    line.write({'name': vals['ref']})
        return result

    @api.model
    def create(self, vals):
        result = super(AccountPayment, self).create(vals)
        if 'ref' in vals:
            if result.move_id:
                result.move_id.line_ids.write({'name': vals['ref']})
        return result


class AccountCheque(models.Model):
    _inherit = "account.cheque"

    ref = fields.Char(string="Memo")

    def write(self, vals):
        result = super(AccountCheque, self).write(vals)
        if 'ref' in vals:
            for rec in self:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': vals['ref']})
        return result

    def set_to_submit(self):
        res = super(AccountCheque, self).set_to_submit()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res
    def set_to_deposite(self):
        res = super(AccountCheque, self).set_to_deposite()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res
    def action_incoming_cashed(self):
        res = super(AccountCheque, self).action_incoming_cashed()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res
    def set_to_return(self):
        res = super(AccountCheque, self).set_to_return()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res
    def set_to_bounced(self):
        res = super(AccountCheque, self).set_to_bounced()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res
    def action_outgoing_cashed(self):
        res = super(AccountCheque, self).action_outgoing_cashed()
        for rec in self:
            if rec.ref:
                journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
                for Jou in journal_item_ids:
                    for line in Jou.line_ids:
                        line.write({'name': rec.ref})
        return res

