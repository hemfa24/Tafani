# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class accountPayment(models.Model):
    _inherit = "account.payment"

    destination_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        domain="['|', ('show_in_payment','=',True), ('account_type', 'in', ('asset_receivable', 'liability_payable')), ('company_id', '=', company_id)]",
        check_company=True
    )