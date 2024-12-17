# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_create_pos_product = fields.Boolean("Enable Product Creation")
