# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class res_users(models.Model):
    _inherit = "res.users"

    pos_login_direct = fields.Boolean("POS Login Direct", help='When user login to Odoo, automatic forward to POS Screen')
    pos_logout_direct = fields.Boolean("POS Logout Direct", help='When user close pos session, automatic logout Odoo')
    pos_config_id = fields.Many2one("pos.config", "POS Config")
    close_cash_popup = fields.Boolean('Close Cash Popup')

    # @api.constrains('pos_config_id')
    # def _check_pos_config_id(self):
    #     if self.search_count([
    #         ('pos_config_id', '=', self.pos_config_id.id),
    #     ]) > 1:
    #         raise ValidationError(_("Another User is already used this point of sale."))
