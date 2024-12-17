# Copyright (C) Softhealer Technologies.
from odoo import fields, models

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_product_suggestion = fields.Boolean(related="pos_config_id.enable_product_suggestion", readonly=False)
    
    pos_enable_refund = fields.Boolean(
        related="pos_config_id.enable_refund", readonly=False)
    pos_enable_info = fields.Boolean(
        related="pos_config_id.enable_info", readonly=False)
    pos_enable_note = fields.Boolean(
        related="pos_config_id.enable_note", readonly=False)
    pos_enable_change_uom = fields.Boolean(
        related="pos_config_id.enable_change_uom", readonly=False)
    pos_enable_quick_order = fields.Boolean(
        related="pos_config_id.enable_quick_order", readonly=False)
    pos_enable_show_order = fields.Boolean(
        related="pos_config_id.enable_show_order", readonly=False)
    pos_enable_auto_pro_uom = fields.Boolean(
        related="pos_config_id.enable_auto_pro_uom", readonly=False)
    pos_enable_variant_popup = fields.Boolean(
        related="pos_config_id.enable_variant_popup", readonly=False)