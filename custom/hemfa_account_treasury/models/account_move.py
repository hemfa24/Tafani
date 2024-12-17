# -*- coding: utf-8 -*-

from odoo import models, fields


class accountMove(models.Model):
    _inherit = "account.move"

    check = fields.Boolean()
    curr_due_amount = fields.Monetary(string='Amount Due', readonly=True)

    # amount_residual = fields.Monetary(
    #     string='Amount Due',
    #     compute='_compute_amount', store=False,
    # )