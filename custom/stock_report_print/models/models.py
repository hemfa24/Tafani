# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def print_valuation_report(self):
        return self.env.ref('stock_report_print.action_print_inventory_stock_report').report_action(self, data=None)

    def _get_report_base_filename(self):
        return 'Inventory Stock Report' + str(fields.Datetime.now().strftime('%Y-%m-%d %H:%M'))

    @api.model
    def get_report_date(self):
        return str(fields.Datetime.now().strftime('%Y-%m-%d %H:%M'))

    total_purchased = fields.Float(
        string='Total Purchase',
        required=False, compute='_compute_totals_purchases')
    total_sales_product = fields.Float(
        string='Total Sold',
        required=False, compute='_compute_totals_sales')

    def _compute_totals_purchases(self):
        domain = [
            ('order_id.state', 'in', ['purchase', 'done']),
            ('product_id', 'in', self.ids),

        ]
        order_lines = self.env['purchase.order.line']._read_group(domain, ['product_id', 'product_uom_qty'],
                                                                  ['product_id'])
        purchased_data = dict([(data['product_id'][0], data['product_uom_qty']) for data in order_lines])
        for product in self:
            if not product.id:
                product.total_purchased = 0.0
                continue
            product.total_purchased = float_round(purchased_data.get(product.id, 0),
                                                  precision_rounding=product.uom_id.rounding)

    def _compute_totals_sales(self):
        r = {}
        self.sales_count = 0

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['sale.report']._read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            if not product.id:
                product.total_sales_product = 0.0
                continue
            product.total_sales_product = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        return r