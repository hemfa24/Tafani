# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    # def _get_in_svl_vals(self, forced_quantity):
    #     result = super(StockMove, self)._get_in_svl_vals(forced_quantity)
    #     move_obj = self.env['stock.move']
    #     for res in result:
    #         if res.get('stock_move_id'):
    #             move_id = move_obj.browse(res.get('stock_move_id'))
    #             if move_id and move_id.purchase_line_id and move_id.purchase_line_id.order_id.discount_type in ['line', 'global']:
    #                 if move_id.purchase_line_id.order_id.purchase_manual_currency_rate_active and move_id.purchase_line_id.order_id.purchase_manual_currency_rate > 0.0:
    #                     res.update({
    #                         'value': move_id.purchase_line_id.price_subtotal * move_id.purchase_line_id.order_id.purchase_manual_currency_rate
    #                     })
    #                 else:
    #                     res.update({
    #                         'value': move_id.purchase_line_id.price_subtotal
    #                     })
    #     print ("resultresult - - -- -", result)
    #     return result
