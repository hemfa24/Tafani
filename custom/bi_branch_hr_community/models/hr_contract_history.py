# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class HrContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    branch_id = fields.Many2one('res.branch', string='Branch')
    