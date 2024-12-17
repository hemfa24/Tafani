from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    gia_mua_hang = fields.Float(
        string="Giá lần trước", related="product_id.standard_price")
    state_color_giamuahang = fields.Selection(selection=[('1', 'black'), ('2', 'red')], compute="_compute_progress",
                                              default="1", invisible=True)

    @api.depends('product_id')
    def _muahang_update(self):
        for line in self:
            value = line['product_id']['id']
            print(line['product_id']['id'])
            lids = self.env['purchase.order.line'].search(
                [('product_id', '=', 2) and ('state', '=', 'purchase')])
            if len(lids) != 0:
                for i in lids:
                    print(i['name'])
            if len(lids) == 0:
                line.gia_mua_hang = 0
            else:
                line.gia_mua_hang = lids[0]['price_unit']

    #      line.update({'gia_mua_hang': lids[0]['price_unit']})
    # @api.depends('price_unit', 'product_id')
    # def _thaydoistate(self):
    #     for line in self:
    #         if line.price_unit > line.gia_mua_hang:
    #             line.state_color_giamuahang = "2"
    #         else:
    #             line.state_color_giamuahang = "1"

    # @api.depends('price_unit', 'product_id')
    # def _compute_progress(self):
    #     for line in self:
    #         if line.price_unit > line.gia_mua_hang:
    #             line.state_color_giamuahang = "2"

    #         else:
    #             line.state_color_giamuahang = "1"


# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     state_giamuahang = fields.Char(
#         string="Cảnh báo", invisible=True, default="")

#     @api.depends('order_line')
#     def _compute_progress(self):
#         if len(self['order_line']) != 0:
#             for line in self['order_line']:
#                 if line.price_unit > line.gia_mua_hang:
#                     self.state_giamuahang = "Giá mua của sản phẩm cao hơn lần trước"
#                     break
