# -*- coding: utf-8 -*-
#################################################################################
# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License OPL-1
#################################################################################
from odoo import api, fields, models, _

class Module(models.Model):
    _inherit = "ir.module.module"

    need_upgrade = fields.Boolean(compute='_compute_module_upgrade', search='_search_need_upgrade',
                                  string="Need Upgrade")

    def _search_need_upgrade(self, operator, value):
        ids = []
        apps = self.env['ir.module.module'].search([('state','=','installed')])
        for app in apps:
            if app.installed_version != app.latest_version:
                ids.append(app.id)
        return [('id', 'in', ids)]

    @api.depends('latest_version')
    def _compute_module_upgrade(self):
        for app in self:
            if app.state == "installed":
                app.need_upgrade = app.installed_version != app.latest_version
