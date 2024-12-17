# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models



class SaleReport(models.Model):
	_inherit = "sale.report"

	bi_margin = fields.Float('Bi Margin')


	def _select_sale(self):
		select_ = f"""
			MIN(l.id) AS id,
			l.product_id AS product_id,
			t.uom_id AS product_uom,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS product_uom_qty,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_delivered / u.factor * u2.factor) ELSE 0 END AS qty_delivered,
			CASE WHEN l.product_id IS NOT NULL THEN SUM((l.product_uom_qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END AS qty_to_deliver,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END AS qty_invoiced,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END AS qty_to_invoice,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_total
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS price_total,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_subtotal
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS price_subtotal,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_to_invoice
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS untaxed_amount_to_invoice,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.untaxed_amount_invoiced
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS untaxed_amount_invoiced,
			COUNT(*) AS nbr,
			s.name AS name,
			s.date_order AS date,
			s.state AS state,
			s.partner_id AS partner_id,
			s.user_id AS user_id,
			s.company_id AS company_id,
			s.campaign_id AS campaign_id,
			s.medium_id AS medium_id,
			s.source_id AS source_id,
			t.categ_id AS categ_id,
			s.pricelist_id AS pricelist_id,
			s.analytic_account_id AS analytic_account_id,
			s.team_id AS team_id,
			p.product_tmpl_id,
			partner.country_id AS country_id,
			partner.industry_id AS industry_id,
			partner.commercial_partner_id AS commercial_partner_id,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(p.weight * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS weight,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(p.volume * l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS volume,
			l.discount AS discount,
			CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_unit * l.product_uom_qty * l.discount / 100.0
				* {self._case_value_or_one('s.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}
				) ELSE 0
			END AS discount_amount,
			SUM(l.margin / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS bi_margin,
			s.id AS order_id"""

		additional_fields_info = self._select_additional_fields()
		template = """,
			%s AS %s"""
		for fname, query_info in additional_fields_info.items():
			select_ += template % (query_info, fname)

		return select_



	def _select_pos(self):
		select_ = f"""
			-MIN(l.id) AS id,
			l.product_id AS product_id,
			t.uom_id AS product_uom,
			SUM(l.qty) AS product_uom_qty,
			SUM(l.qty) AS qty_delivered,
			0 AS qty_to_deliver,
			CASE WHEN pos.state = 'invoiced' THEN SUM(l.qty) ELSE 0 END AS qty_invoiced,
			CASE WHEN pos.state != 'invoiced' THEN SUM(l.qty) ELSE 0 END AS qty_to_invoice,
			SUM(l.price_subtotal_incl)
				* MIN({self._case_value_or_one('pos.currency_rate')})
				* {self._case_value_or_one('currency_table.rate')}
			AS price_total,
			SUM(l.price_subtotal)
				* MIN({self._case_value_or_one('pos.currency_rate')})
				* {self._case_value_or_one('currency_table.rate')}
			AS price_subtotal,
			(CASE WHEN pos.state != 'invoiced' THEN SUM(l.price_subtotal) ELSE 0 END)
				* MIN({self._case_value_or_one('pos.currency_rate')})
				* {self._case_value_or_one('currency_table.rate')}
			AS amount_to_invoice,
			(CASE WHEN pos.state = 'invoiced' THEN SUM(l.price_subtotal) ELSE 0 END)
				* MIN({self._case_value_or_one('pos.currency_rate')})
				* {self._case_value_or_one('currency_table.rate')}
			AS amount_invoiced,
			count(*) AS nbr,
			pos.name AS name,
			pos.date_order AS date,
			CASE WHEN pos.state = 'draft' THEN 'pos_draft' WHEN pos.state = 'done' THEN 'pos_done' else pos.state END AS state,
			pos.partner_id AS partner_id,
			pos.user_id AS user_id,
			pos.company_id AS company_id,
			NULL AS campaign_id,
			NULL AS medium_id,
			NULL AS source_id,
			t.categ_id AS categ_id,
			pos.pricelist_id AS pricelist_id,
			NULL AS analytic_account_id,
			pos.crm_team_id AS team_id,
			p.product_tmpl_id,
			partner.country_id AS country_id,
			partner.industry_id AS industry_id,
			partner.commercial_partner_id AS commercial_partner_id,
			(SUM(p.weight) * l.qty / u.factor) AS weight,
			(SUM(p.volume) * l.qty / u.factor) AS volume,
			l.discount AS discount,
			SUM((l.price_unit * l.discount * l.qty / 100.0
				* {self._case_value_or_one('pos.currency_rate')}
				* {self._case_value_or_one('currency_table.rate')}))
			AS discount_amount,
			SUM(l.margin / CASE COALESCE(pos.currency_rate, 0) WHEN 0 THEN 1.0 ELSE pos.currency_rate END) AS bi_margin,
			NULL AS order_id"""

		additional_fields = self._select_additional_fields()
		additional_fields_info = self._fill_pos_fields(additional_fields)
		template = """,
			%s AS %s"""
		for fname, value in additional_fields_info.items():
			select_ += template % (value, fname)
		return select_