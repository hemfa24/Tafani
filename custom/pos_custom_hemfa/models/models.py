# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_sync_product = fields.Boolean(string="Allow Sync Product")
    opening_cash = fields.Float(string="Openning Cash ", default=0.0)
    default_cash = fields.Boolean(string="Default Cash Amount")


class PosSession(models.Model):
    _inherit = "pos.session"

    cash_counted = fields.Float(string="Cash", store=True, readonly=True)
    bank_counted = fields.Float(string="Bank", store=True, readonly=True)
    other_counted = fields.Float(string="Other", store=True, readonly=True)
    close_custom = fields.One2many("custom.session.close.data", "session_id")

    def set_record_val(self, cash_val, bank_val):
        self.ensure_one()
        self.cash_counted = cash_val
        self.bank_counted = bank_val
        self.state = "closing_control"
        return {"successful": True}


class PosclossData(models.Model):
    _name = "custom.session.close.data"

    session_id = fields.Many2one("pos.session")
    payment_method = fields.Many2one(
        "pos.payment.method", string=" ", store=True, readonly=True
    )
    custom_expected = fields.Float(string="  ", store=True, readonly=True)
    custom_counted = fields.Float(string="  ", store=True)
    custom_difference = fields.Float(
        string="     ", store=True, readonly=True, compute="_compute_cuomt"
    )

    @api.depends("custom_counted")
    def _compute_cuomt(self):
        res = self.get_external_id()
        for record in self:
            record.custom_difference = record.custom_expected - record.custom_counted
