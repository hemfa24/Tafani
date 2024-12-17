# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        self.check_storekeeper()
        return super(StockPicking, self).button_validate()

    def check_storekeeper(self):
        if self.picking_type_id.code == 'internal' and self.state == 'draft':
            employee_ids = self.location_id.warehouse_id.storekeeper_ids.filtered(lambda r: r.user_id == self.env.user)
            if not employee_ids:
                raise UserError(_('you are not storekeeper for stock location source .'))