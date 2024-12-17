# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
###############################################################################
from odoo import models, fields, api, _


class product_template(models.Model):
    _inherit = 'product.template'


    allow_sales_user_ids = fields.Many2many('res.users','product_template_res_sales_user_rel','product_id','user_id','Allow Sales Person')


