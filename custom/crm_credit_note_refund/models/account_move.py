# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    custom_credit_note_crm_id = fields.Many2one(
        'crm.lead',
        string='CRM Reference',
        copy=False,
        states={
            'posted': [('readonly', True)],
            'cancel': [('readonly', True)]
        },
    )
   

    # def _reverse_move_vals(self, default_values, cancel=True):
    #     move_vals = super(AccountMove, self)._reverse_move_vals(default_values=default_values, cancel=cancel)
    #     if self._context.get('custom_credit_note_crm_id'):
    #         move_vals.update({
    #             'custom_credit_note_crm_id': int(self._context.get('custom_credit_note_crm_id')),
    #         })
    #     return move_vals

    def _reverse_moves(self, default_values_list=None, cancel=False):
        move_vals = super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        if self._context.get('custom_credit_note_crm_id'):
            move_vals.update({
                'custom_credit_note_crm_id': int(self._context.get('custom_credit_note_crm_id')),
            })
        return move_vals



    def action_reverse(self):
        res = super(AccountMove, self).action_reverse()
        if self._context.get('active_model') == 'crm.lead':
            res['context'] = {
                'active_model': 'account.move',
                'active_ids': self._context.get('active_move_id'),
                'active_id': self._context.get('active_move_id'),
                'custom_credit_note_crm_id': self._context.get('active_id')
            }
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
