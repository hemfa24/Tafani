# -*- coding: utf-8 -*-

# from odoo import models, fields, api
#
#
# class accountAccount(models.Model):
#     _inherit = 'account.account'
#
#     is_internal_transfer_account = fields.Boolean('Is Intrenal Transfere Cash Account')

# class resCompany(models.Model):
#     _inherit = 'res.company'

#     # transfer_cash_account_id = fields.Many2one('account.account',
#     #     domain=lambda self: [('reconcile', '=', True), 
#     #     ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id),
#     #      ('deprecated', '=', False)],
#     #       string="Inter-Cash Transfer Account", help="Intermediary account used when moving money from a liquidity account to another")
    
    
#     is_transfer_cash = fields.Boolean()