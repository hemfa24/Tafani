# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
# import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import UserError
import json
from odoo.tools import float_is_zero, float_compare

class AccountCheque(models.Model):
	_inherit = "account.cheque"
	
	manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
	manual_currency_rate = fields.Float('Rate', digits=(12, 6))
	currency_id = fields.Many2one('res.currency', "Currency", default=(lambda self:self.env.user.company_id.currency_id.id))
	
	@api.constrains('manual_currency_rate_active','currency_id')
	def constrains_manual_currency_rate_active(self):
		for rec in self:
			if rec.manual_currency_rate_active and rec.currency_id.id == self.env.user.company_id.currency_id.id:
				raise UserError(_('Company currency and Cheque currency same, You can not added manual Exchange rate in same currency.'))


	@api.onchange('manual_currency_rate_active')
	def onchange_manual_currency_rate_active(self):
		for rec in self:
			if not rec.manual_currency_rate_active:
				rec.currency_id = self.env.user.company_id.currency_id.id


	def action_incoming_cashed(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
				{
				'default_manual_currency_rate':self.manual_currency_rate,
				'default_manual_currency_rate_active':self.manual_currency_rate_active,
				'default_currency_id':self.currency_id.id,
				'is_check':True
				}
				)
		res = super(AccountCheque,self).action_incoming_cashed()

		return res
		
	def action_outgoing_cashed(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
				{
				'default_manual_currency_rate':self.manual_currency_rate,
				'default_manual_currency_rate_active':self.manual_currency_rate_active,
				'default_currency_id':self.currency_id.id,
				'is_check':True
				}
				)
		res = super(AccountCheque,self).action_outgoing_cashed()
		
		return res



	def set_from_deposite_to_draft(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).set_from_deposite_to_draft()
		
		return res

	def set_to_submit(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).set_to_submit()
		
		
		return res
		

	def set_to_bounced(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).set_to_bounced()
		
		
		return res


	
	def action_incoming_return_to_deposited(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).action_incoming_return_to_deposited()
		
		
		return res
	
	

	def set_to_return(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).set_to_return()

		return res
		

	def set_to_deposite(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
			{
			'default_manual_currency_rate':self.manual_currency_rate,
		 	'default_manual_currency_rate_active':self.manual_currency_rate_active,
			'default_currency_id':self.currency_id.id,
			'is_check':True
			}
			)
		res = super(AccountCheque,self).set_to_deposite()
		return res

		          

