# -*- coding: utf-8 -*-

from odoo import _, _lt, api, fields, models
from odoo.exceptions import UserError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    storekeeper_ids = fields.Many2many('hr.employee',
                                       'stock_warehouse_storekeeper_rel',
                                       'warehouse_id', 'employee_id',
                                       string='Storekeepers')

