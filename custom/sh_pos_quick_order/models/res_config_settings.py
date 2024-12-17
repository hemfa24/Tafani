# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_is_enable_quick_order = fields.Boolean(
        related="pos_config_id.sh_is_enable_quick_order", readonly=False)
    pos_sh_is_enable_quick_invoice = fields.Boolean(
        related="pos_config_id.sh_is_enable_quick_invoice", readonly=False)
    pos_sh_quick_customer = fields.Many2one(
        related="pos_config_id.sh_quick_customer", readonly=False)
    pos_sh_is_quick_payment_method = fields.Many2one(
        related="pos_config_id.sh_is_quick_payment_method", readonly=False)