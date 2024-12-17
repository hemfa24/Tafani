# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval


class Company(models.Model):
    _inherit = 'res.company'
	
    in_credit_account_id = fields.Many2one('account.account',string="Credit Account")
    in_debit_account_id = fields.Many2one('account.account',string="Debit Account")
    
    out_credit_account_id = fields.Many2one('account.account',string="Credit Account")
    out_debit_account_id = fields.Many2one('account.account',string="Debit Account")
    
    deposite_account_id = fields.Many2one('account.account',string="Deposite Account")
    specific_journal_id = fields.Many2one('account.journal',string="Specific Journal")
    	        
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    in_credit_account_id = fields.Many2one('account.account',string="Credit Account",related="company_id.in_credit_account_id",readonly=False)
    in_debit_account_id = fields.Many2one('account.account',string="Debit Account",related="company_id.in_debit_account_id",readonly=False)
    
    out_credit_account_id = fields.Many2one('account.account',string="Credit Account",related="company_id.out_credit_account_id",readonly=False)
    out_debit_account_id = fields.Many2one('account.account',string="Debit Account",related="company_id.out_debit_account_id",readonly=False)
    
    deposite_account_id = fields.Many2one('account.account',string="Deposite Account",related="company_id.deposite_account_id",readonly=False)
    specific_journal_id = fields.Many2one('account.journal',string="Specific Journal",related="company_id.specific_journal_id",readonly=False)
    