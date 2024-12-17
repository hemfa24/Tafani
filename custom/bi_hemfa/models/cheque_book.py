# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChequeBook(models.Model):
    _inherit = "cheque.book"

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
