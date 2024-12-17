# Copyright © 2023 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models


class PrintProductLabelLine(models.TransientModel):
    _inherit = "print.product.label.line"

    price = fields.Float(digits='Products Price', default=0.0, readonly=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
    )

    @api.depends('product_id', 'wizard_id.pricelist_id')
    def _compute_currency_id(self):
        with_product = self.filtered('product_id')
        for line in with_product:
            # flake8: noqa: E501
            pricelist = line.wizard_id.pricelist_id
            line.price = pricelist and pricelist._get_product_price(line.product_id, 0) or line.product_id.lst_price
            line.currency_id = pricelist and pricelist.currency_id.id or line.product_id.currency_id.id
        (self - with_product).price = False
        (self - with_product).currency_id = False
