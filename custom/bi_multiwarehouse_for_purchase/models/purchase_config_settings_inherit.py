	# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _



class ResCompany(models.Model):
	_inherit = 'res.company'


	allow_purchase_warehouse = fields.Boolean(string="Allow Warehouse in Purchase Order Line", default=False)


class ResConfigSettings(models.TransientModel): 
	_inherit = 'res.config.settings'


	allow_purchase_warehouse = fields.Boolean(string="Allow Warehouse in Purchase Order Line", related='company_id.allow_purchase_warehouse',readonly=False,)






