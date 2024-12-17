# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_
from odoo.exceptions import UserError, Warning
from functools import lru_cache
from odoo.tools import float_is_zero, OrderedSet
from odoo.tools.float_utils import float_round, float_is_zero, float_compare


class resCompany(models.Model):
	_inherit ='res.company'

	active_bill_recompute_cost = fields.Boolean()

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	active_bill_recompute_cost = fields.Boolean(related="company_id.active_bill_recompute_cost",readonly=0)

class account_invoice_line(models.Model):
	_inherit ='account.move.line'


	@api.depends('currency_id', 'company_id', 'move_id.date')
	def _compute_currency_rate(self):
        
		@lru_cache()
		def get_rate(from_currency, to_currency, company, date):
			result = self.env['res.currency']._get_conversion_rate(
				from_currency=from_currency,
				to_currency=to_currency,
				company=company,
				date=date,
			)
			if line.move_id.manual_currency_rate_active and line.move_id.manual_currency_rate > 0:
				result = line.company_id.currency_id.rate / line.move_id.manual_currency_rate
			
			return result
		for line in self:
			line.currency_rate = get_rate(
				from_currency=line.company_currency_id,
				to_currency=line.currency_id,
				company=line.company_id,
				date=line.move_id.invoice_date or line.move_id.date or fields.Date.context_today(line),
			)
	
	@api.onchange('product_id')
	def _onchange_product_id_set_manual_currencyy_rate(self):
		for line in self:
			line._compute_currency_rate()
			line._compute_amount_currency()
			
	def _create_in_invoice_svl(self):
		print("_create_in_invoice_svl")
		if not self.env.user.company_id.active_bill_recompute_cost:
			return self.env['stock.valuation.layer'].search([('id','=',-1)])
		else:
			# super(account_invoice_line,self)._create_in_invoice_svl()
			svl_vals_list = []
			for line in self:
				line = line.with_company(line.company_id)
				move = line.move_id.with_company(line.move_id.company_id)
				po_line = line.purchase_line_id
				uom = line.product_uom_id or line.product_id.uom_id

				# Don't create value for more quantity than received
				quantity = po_line.qty_received - (po_line.qty_invoiced - line.quantity)
				quantity = max(min(line.quantity, quantity), 0)
				if float_is_zero(quantity, precision_rounding=uom.rounding):
					continue

				layers = line._get_stock_valuation_layers(move)
				# Retrieves SVL linked to a return.
				if not layers:
					continue

				price_unit = line._get_gross_unit_price()
				price_unit = line.currency_id._convert(price_unit, line.company_id.currency_id, line.company_id, line.date, round=False)
				
				# price_unit = line.currency_id._convert(price_unit, line.company_id.currency_id, line.company_id, line.date, round=False)
				if line.move_id.manual_currency_rate_active and line.move_id.currency_id.id == self.env.user.company_id.currency_id.id:
					price_unit = line._get_gross_unit_price() * line.move_id.manual_currency_rate
				
				
				price_unit = line.product_uom_id._compute_price(price_unit, line.product_id.uom_id)
				layers_price_unit = line._get_stock_valuation_layers_price_unit(layers)
				layers_to_correct = line._get_stock_layer_price_difference(layers, layers_price_unit, price_unit)
				svl_vals_list += line._prepare_in_invoice_svl_vals(layers_to_correct)
			return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

	def _apply_price_difference(self):
		if self:
			line = self[0]
			if line.move_id and line.move_id.manual_currency_rate_active:
				return self.env['stock.valuation.layer'].sudo(), self.env['account.move.line'].sudo()
		lines = []
		for l in self:
			lines.append(l._get_valued_in_moves())
		if lines:
			return self.env['stock.valuation.layer'].sudo(), self.env['account.move.line'].sudo()
		return super(account_invoice_line, self)._apply_price_difference()


class account_invoice(models.Model):
	_inherit ='account.move'

	def _post(self, soft=True):
		"""
		for cheque
		"""
		res = super(account_invoice,self.with_context(no_exchange_difference=True))._post(soft)
		for rec in self:
			if self._context.get('is_check',False) and self._context.get('default_manual_currency_rate_active',False):

				manual_currency_rate_active = self._context.get('default_manual_currency_rate_active',False)
				manual_currency_rate = self._context.get('default_manual_currency_rate',False)
				for line in rec.line_ids:
					line = line.with_context(check_move_validity=False)
					amount = line.move_id.account_cheque_id.amount
					if line.debit > 0:
						
						line.amount_currency = amount
						line.debit = manual_currency_rate * amount
					elif line.credit > 0:
						
						line.amount_currency = -amount
						line.credit = manual_currency_rate * amount
			
			if self._context.get('is_landed_cost',False) and self._context.get('default_manual_currency_rate_active',False):

				manual_currency_rate_active = self._context.get('default_manual_currency_rate_active',False)
				manual_currency_rate = self._context.get('default_manual_currency_rate',False)
				for line in rec.line_ids:
					line = line.with_context(check_move_validity=False)
					line.currency_id = self._context.get('default_currency_id',False)
					if line.debit > 0:
						amount = line.debit
					
						
						# line.amount_currency = amount
						line.debit = manual_currency_rate * amount
					elif line.credit > 0:
						amount = line.credit
						
						# line.amount_currency = -amount
						line.credit = manual_currency_rate * amount
						
		return res

	manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
	manual_currency_rate = fields.Float('Rate', digits=(12, 6))

	@api.onchange('manual_currency_rate_active')
	def _onchange_manual_currency_rate_active(self):
		for rec in self:
			if rec.manual_currency_rate_active:
				rec.currency_id = False
			else:
				rec.currency_id = self.env.company.currency_id.id

	@api.constrains("manual_currency_rate")
	def _check_manual_currency_rate(self):
		for record in self:
			if record.manual_currency_rate_active:
				if record.manual_currency_rate == 0:
					raise UserError(_('Exchange Rate Field is required , Please fill that.'))
				else:
					record.line_ids._compute_currency_rate()
					record.line_ids._compute_amount_currency()

	@api.onchange('manual_currency_rate_active', 'currency_id')
	def check_currency_id(self):
		if self.manual_currency_rate_active:
			if self.currency_id == self.company_id.currency_id:
				self.manual_currency_rate_active = False
				raise UserError(_('Company currency and invoice currency same, You can not added manual Exchange rate in same currency.'))
			else:
				self.line_ids._compute_currency_rate()
				self.line_ids._compute_amount_currency()



#next code is in base but i commented

class StockMove(models.Model):
	_inherit = 'stock.move'


	def _get_price_unit(self):
		""" Returns the unit price for the move"""
		self.ensure_one()
		if not self.purchase_line_id or not self.product_id.id:
			return super(StockMove, self)._get_price_unit()
		print ("Call Heriir -- -- - -- -- -- - -----")
		price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
		line = self.purchase_line_id
		order = line.order_id
		received_qty = line.qty_received
		if self.state == 'done':
			received_qty -= self.product_uom._compute_quantity(self.quantity_done, line.product_uom)
		print("line.qty_invoiced", line.qty_invoiced)
		if float_compare(line.qty_invoiced, received_qty, precision_rounding=line.product_uom.rounding) > 0:
			print("1")
			move_layer = line.move_ids.stock_valuation_layer_ids
			invoiced_layer = line.invoice_lines.stock_valuation_layer_ids
			print ("1", sum(move_layer.mapped('value')))
			print("2-1", sum(invoiced_layer.mapped('value')))
			receipt_value = sum(move_layer.mapped('value')) + sum(invoiced_layer.mapped('value'))
			invoiced_value = 0
			invoiced_qty = 0
			print("line.sudo().invoice_lines", line.sudo().invoice_lines)
			for invoice_line in line.sudo().invoice_lines:
				print ("invoice_line.price_unit--------------", line.price_unit, invoice_line.quantity)
				# if invoice_line.move_id.state != 'posted':
				# 	continue
				if invoice_line.tax_ids:
					invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
						line.price_unit, currency=invoice_line.currency_id, quantity=invoice_line.quantity)['total_void']
					print ("invoiced_value --  A", invoiced_value)
				else:
					print("invoice_line.price_unit ----------", line.price_unit, invoice_line.quantity)
					invoiced_value += line.price_unit * invoice_line.quantity
					print(".....1", invoiced_value)
				invoiced_qty += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_id.uom_id)
				print ("invoiced_qty --00000", invoiced_qty)
			# TODO currency check
			print(".|||..............invoiced_value..", invoiced_value, receipt_value)
			if order.purchase_manual_currency_rate_active:
				invoiced_value = invoiced_value * order.purchase_manual_currency_rate
			print ("---New ", invoiced_value)
			remaining_value = abs(invoiced_value - receipt_value)
			print("remaining_value", remaining_value)
			# TODO qty_received in product uom
			remaining_qty = invoiced_qty - line.product_uom._compute_quantity(received_qty, line.product_id.uom_id)
			print("remaining_qty", remaining_qty, remaining_qty)
			price_unit = float_round(remaining_value / remaining_qty, precision_digits=price_unit_prec)
			print("price_unit", price_unit)
		# --------- NEEED CALL TO HERE
		else:
			print("2")
			price_unit = line.price_unit
			if order.purchase_manual_currency_rate_active:
				price_unit = line.price_unit * line.order_id.purchase_manual_currency_rate
			if line.taxes_id:
				qty = line.product_qty or 1
				price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
				price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
			if line.product_uom.id != line.product_id.uom_id.id:
				price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
			print("------ 249 - - -- -- -- -- -- - -", price_unit)
		# if order.currency_id != order.company_id.currency_id:
		# 	print("3", price_unit)
		# 	# The date must be today, and not the date of the move since the move move is still
		# 	# in assigned state. However, the move date is the scheduled date until move is
		# 	# done, then date of actual move processing. See:
		# 	# https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
		# 	if order.purchase_manual_currency_rate_active:
		# 		price_unit = price_unit * line.order_id.purchase_manual_currency_rate
		# 		print("3-----")
		# 	else:	
		# 		price_unit = order.currency_id._convert(
		# 			price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
		# print("price_unit - -- - - - -", price_unit	)
		#STOP
		return price_unit












# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
