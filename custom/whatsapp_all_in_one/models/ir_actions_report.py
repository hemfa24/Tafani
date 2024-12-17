# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def get_paperformat(self):
        res = super(IrActionsReport, self).get_paperformat()
        pos_receipt_paperformat_id = self.env.context.get('pos_receipt_paperformat_id')
        return pos_receipt_paperformat_id or res
