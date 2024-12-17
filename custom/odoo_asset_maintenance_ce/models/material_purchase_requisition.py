# -*- coding: utf-8 -*-

from odoo import models, fields


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    maintenance_id = fields.Many2one(
        'maintenance.request',
        string='Maintenance Request',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
