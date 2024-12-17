# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class AccounMoveIhert(models.Model):
    _inherit = 'account.move'

    type_flag = fields.Boolean(store=True, readonly=True, default=False)
    # type_flag_refund = fields.Boolean(store=True, readonly=True)

    def inhert_action_post(self):
        self.sudo().write({
            'state': 'posted',
            'posted_before': True,
        })
