# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
################################################################################

from odoo import tools
from odoo import models, fields, api

class AccountInvoiceReport(models.Model):
	_inherit = "account.invoice.report"

	margin_subtotal_signed = fields.Float('Margin')

	def _select(self):
		return super()._select() + ",line.margin_subtotal_signed AS margin_subtotal_signed"