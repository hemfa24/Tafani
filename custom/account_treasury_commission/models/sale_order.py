from odoo import api, fields, models, tools, _
from docutils.nodes import field
from odoo.exceptions import ValidationError, Warning
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_id', 'user_id')
    def _compute_team_id(self):
        super(SaleOrder, self)._compute_team_id()
        for order in self:
            if order.user_id:
                default_sale_commission = self.env['sale.commission']
                default_commission = default_sale_commission.search([
                    ('compute_for', '=', 'sales_person'), ('user_ids', 'in', order.user_id.ids)], limit=1)
                if default_commission:
                    order.sale_commission_id = default_commission.id


    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'sale_commission_id': self.sale_commission_id.id,
        })
        return result

