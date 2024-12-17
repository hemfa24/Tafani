# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
###############################################################################
from odoo import fields,models,api,_


class kits_assigne_sales_person_to_product_wizard(models.TransientModel):
    _name = 'kits.assigne.sales.person.to.product.wizard'
    _description = 'Assign Sales Person To Products wizard'

    user_ids = fields.Many2many('res.users',string='Sales Person')



    def action_assigne_sales_person(self):
        active_id = self._context.get('active_ids')
        if active_id:
            for product in self.env['product.template'].browse(active_id):
                product.allow_sales_user_ids = [(6, 0, self.user_ids.ids)]