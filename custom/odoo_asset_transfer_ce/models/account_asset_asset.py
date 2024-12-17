# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class account_asset_asset(models.Model):
    _inherit = "account.asset.asset.custom"

#    @api.multi
    def action_view_asset_transfer(self):
        self.ensure_one()
        transferred_asset_ids = self.env['asset.accountability.transfer'].search([('transferred_asset_id', '=', self.id)])
        action = self.env.ref('odoo_asset_transfer_ce.act_asset_accountability_transfer').sudo().read()[0]
        action['domain'] = [('id', 'in', transferred_asset_ids.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
