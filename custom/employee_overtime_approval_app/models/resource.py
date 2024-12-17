# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    days_per_month = fields.Integer('AVG Day per Month', required=True, default=30)
