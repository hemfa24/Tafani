# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_sale_plan = fields.Boolean("Sales Plan Active", implied_group='hemfa_sale_plan.group_sale_plan')
    

    def set_values(self):
        super().set_values()
        