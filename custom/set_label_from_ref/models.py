# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _




class AccountAccountType(models.Model):
    _inherit = "account.move.line"

    ref_exist = fields.Boolean(string="ref", compute='_compute_ref_val')

    @api.depends('move_id', 'move_id.ref')
    def _compute_ref_val(self):
        for rec in self:
            if rec.move_id and rec.move_id.ref:
                rec.ref_exist=True
                rec.name = rec.move_id.ref
            else:
                rec.ref_exist = False
                #rec.write({'name': ''})