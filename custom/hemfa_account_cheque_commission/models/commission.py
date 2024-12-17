 # -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleCommissionlines(models.Model):
    _inherit = 'sale.commission.lines'

    cheque_id = fields.Many2one(
        'account.cheque',
        string='Checks',
        copy=False
    )



