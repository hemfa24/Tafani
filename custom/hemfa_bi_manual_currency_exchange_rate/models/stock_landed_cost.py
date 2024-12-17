# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
# import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import json
from odoo.tools import float_is_zero, float_compare


from collections import defaultdict


class StockMove(models.Model):
	_inherit = 'stock.move'

	def _get_in_svl_vals(self, forced_quantity):
		result = super()._get_in_svl_vals(forced_quantity)
		print ("\n\nn\n\nn\\ My calresultresultresult", result)
		move_obj = self.env['stock.move']
		for res in result:
			if res.get('stock_move_id'):
				move_id = move_obj.browse(res.get('stock_move_id'))
				purchase_line_id = move_id.purchase_line_id
				#if move_id and purchase_line_id and purchase_line_id.order_id.discount_type in ['line', 'global']:
				if move_id and purchase_line_id and hasattr(purchase_line_id.order_id, 'discount_type') and purchase_line_id.order_id.discount_type in ['line', 'global']:
					manual_currency_rate_active = purchase_line_id.order_id.purchase_manual_currency_rate_active
					manual_currency_rate = purchase_line_id.order_id.purchase_manual_currency_rate
					if manual_currency_rate_active and manual_currency_rate > 0.0:
						unit_cost = purchase_line_id.price_unit * manual_currency_rate
						res.update({
							'unit_cost': unit_cost,
							'value': unit_cost * res.get('quantity')
						})
					else:
						unit_cost = purchase_line_id.price_unit
						res.update({
							'unit_cost': unit_cost,
							'value': unit_cost * res.get('quantity')
						})
		print ("\n AFTER CALL MYRESUlt", result)
		return result


class AdjustmentLines(models.Model):
	_inherit = 'stock.valuation.adjustment.lines'
	
	currency_id = fields.Many2one('res.currency', related='cost_id.currency_id')
		
class stockLandedCost(models.Model):
	_inherit = "stock.landed.cost"
	

	manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
	manual_currency_rate = fields.Float('Rate', digits=(12, 6))
	# currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
	currency_id = fields.Many2one('res.currency', "Currency",related=False, default=(lambda self:self.env.user.company_id.currency_id.id))
	
	@api.constrains('manual_currency_rate_active','currency_id')
	def constrains_manual_currency_rate_active(self):
		for rec in self:
			if rec.manual_currency_rate_active and (rec.currency_id == False or rec.currency_id.id == self.env.user.company_id.currency_id.id):
				raise UserError(_('Company currency and Cost currency same or not selected, You can not added manual Exchange rate in same currency.'))
			if rec.manual_currency_rate_active and rec.manual_currency_rate <= 0.0:
				raise ValidationError(_("Sorry, Manual Currency Exchange rate must be Greater then 0."))

	@api.onchange('manual_currency_rate_active')
	def onchange_manual_currency_rate_active(self):
		for rec in self:
			if not rec.manual_currency_rate_active:
				rec.currency_id = self.env.user.company_id.currency_id.id


	# def button_validate(self):
	# 	if self.manual_currency_rate_active:
	# 		self = self.with_context(
	# 			{
	# 			'default_manual_currency_rate':self.manual_currency_rate,
	# 			'default_manual_currency_rate_active':self.manual_currency_rate_active,
	# 			'default_currency_id':self.currency_id.id,
	# 			'is_landed_cost':True
	# 			}
	# 			)
	# 	res = super(stockLandedCost,self).button_validate()

	# 	return res


	def button_validate(self):
		if self.manual_currency_rate_active:
			self = self.with_context(
				{
				'default_manual_currency_rate':self.manual_currency_rate,
				'default_manual_currency_rate_active':self.manual_currency_rate_active,
				'default_currency_id':self.currency_id.id,
				'is_landed_cost':True
				}
				)
		self._check_can_validate()
		cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
		if cost_without_adjusment_lines:
			cost_without_adjusment_lines.compute_landed_cost()
		if not self._check_sum():
			raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

		for cost in self:
			cost = cost.with_company(cost.company_id)
			move = self.env['account.move']
			move_vals = {
				'journal_id': cost.account_journal_id.id,
				'date': cost.date,
				'ref': cost.name,
				'line_ids': [],
				'move_type': 'entry',
			}
			valuation_layer_ids = []
			cost_to_add_byproduct = defaultdict(lambda: 0.0)
			for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
				remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
				linked_layer = line.move_id.stock_valuation_layer_ids[:1]

				# Prorate the value at what's still in stock
				cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
				print ("\n\\n\n\n cost_to_addcost_to_addcost_to_addcost_to_addcost_to_add", cost_to_add)
				if not cost.company_id.currency_id.is_zero(cost_to_add):
					valuation_layer = self.env['stock.valuation.layer'].create({
						'value': cost_to_add,
						'unit_cost': 0,
						'quantity': 0,
						'remaining_qty': 0,
						'stock_valuation_layer_id': linked_layer.id,
						'description': cost.name,
						'stock_move_id': line.move_id.id,
						'product_id': line.move_id.product_id.id,
						'stock_landed_cost_id': cost.id,
						'company_id': cost.company_id.id,
					})
					linked_layer.remaining_value += cost_to_add
					valuation_layer_ids.append(valuation_layer.id)
				# Update the AVCO
				product = line.move_id.product_id
				if product.cost_method == 'average':
					cost_to_add_byproduct[product] += cost_to_add
				# Products with manual inventory valuation are ignored because they do not need to create journal entries.
				if product.valuation != "real_time":
					continue
				# `remaining_qty` is negative if the move is out and delivered proudcts that were not
				# in stock.
				qty_out = 0
				if line.move_id._is_in():
					qty_out = line.move_id.product_qty - remaining_qty
				elif line.move_id._is_out():
					qty_out = line.move_id.product_qty
				move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

			# batch standard price computation avoid recompute quantity_svl at each iteration
			products = self.env['product.product'].browse(p.id for p in cost_to_add_byproduct.keys())
			for product in products:  # iterate on recordset to prefetch efficiently quantity_svl
				if not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
					cost_in_product = cost_to_add_byproduct[product] / product.quantity_svl
					if cost.manual_currency_rate_active:
						cost_in_product = cost_in_product * cost.manual_currency_rate

					product.with_company(cost.company_id).sudo().with_context(disable_auto_svl=True).standard_price += cost_in_product
					
			move_vals['stock_valuation_layer_ids'] = [(6, None, valuation_layer_ids)]
			# We will only create the accounting entry when there are defined lines (the lines will be those linked to products of real_time valuation category).
			cost_vals = {'state': 'done'}
			if move_vals.get("line_ids"):
				move = move.create(move_vals)
				cost_vals.update({'account_move_id': move.id})
			cost.write(cost_vals)
			if cost.account_move_id:
				move._post()

			if cost.vendor_bill_id and cost.vendor_bill_id.state == 'posted' and cost.company_id.anglo_saxon_accounting:
				all_amls = cost.vendor_bill_id.line_ids | cost.account_move_id.line_ids
				for product in cost.cost_lines.product_id:
					accounts = product.product_tmpl_id.get_product_accounts()
					input_account = accounts['stock_input']
					all_amls.filtered(lambda aml: aml.account_id == input_account and not aml.reconciled).reconcile()

		return True
	

class StockMove(models.Model):
	_inherit = 'stock.move'

	def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
		self.ensure_one()
		relt = super()._prepare_account_move_vals(
			credit_account_id=credit_account_id,
			debit_account_id=debit_account_id,
			journal_id=journal_id,
			qty=qty,
			description=description,
			svl_id=svl_id,
			cost=cost)
		if self.purchase_line_id:
			relt.update({
				'currency_id': self.purchase_line_id.currency_id.id,
				'manual_currency_rate_active': self.purchase_line_id.order_id.purchase_manual_currency_rate_active,
				'manual_currency_rate': self.purchase_line_id.order_id.purchase_manual_currency_rate,
			})
		return relt
	
	def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
		relt = super()._generate_valuation_lines_data(
			partner_id=partner_id,
			qty=qty,
			debit_value=debit_value,
			credit_value=credit_value,
			debit_account_id=debit_account_id,
			credit_account_id=credit_account_id,
			svl_id=svl_id,
			description=description)
		if self.purchase_line_id:
			cost_price = self.purchase_line_id.price_unit * self.quantity_done
			currency_rate = self.purchase_line_id.order_id.purchase_manual_currency_rate
			relt['credit_line_vals'].update({
				'amount_currency': -1 * cost_price,
				'balance': -1 * (cost_price * currency_rate)
			})
			relt['debit_line_vals'].update({
				'amount_currency': cost_price,
				'balance': cost_price * currency_rate
			})
		return relt
