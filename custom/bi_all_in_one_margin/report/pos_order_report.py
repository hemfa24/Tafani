# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
	_inherit = "report.pos.order"

	cost_price_total = fields.Float(string='Cost Price Total')
	cost_price_unit = fields.Float(string='Cost Price/Unit')
	profit_sale_price = fields.Float(string='Profit(Sale Price-Cost Price)')
	total_profit = fields.Float(string='Total Profit(Total Sales - Total Cost)')

	def _select(self):
		return """
			SELECT
				MIN(l.id) AS id,
				COUNT(*) AS nbr_lines,
				s.date_order AS date,
				SUM(l.qty) AS product_qty,
				SUM(l.margin) AS margin,
				SUM(l.margin) AS total_profit,
				SUM(l.qty * l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_sub_total,
				SUM(l.purchase_price / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS cost_price_unit,
				SUM((l.qty * l.price_unit) * (100 - l.discount) / 100 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_total,
				SUM((l.price_unit - l.purchase_price) * (100 - l.purchase_price) / 100 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS profit_sale_price,
				SUM((l.qty * l.price_unit) * (100 - l.discount) / 100 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS cost_price_total,
				SUM((l.qty * l.price_unit) * (l.discount / 100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_discount,
				(SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal AS average_price,
				SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
				s.id as order_id,
				s.partner_id AS partner_id,
				s.state AS state,
				s.user_id AS user_id,
				s.company_id AS company_id,
				s.sale_journal AS journal_id,
				l.product_id AS product_id,
				pt.categ_id AS product_categ_id,
				p.product_tmpl_id,
				ps.config_id,
				pt.pos_categ_id,
				s.pricelist_id,
				s.session_id,
				s.account_move IS NOT NULL AS invoiced
		"""
