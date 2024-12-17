from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    weight = fields.Float(string="Weight(kg)", compute="_compute_weight")

    @api.onchange('product_id')
    def onchange_product_weight(self):
        for product in self:
            product.weight = product.product_id.weight

    def _compute_weight(self):
        for line in self:
            weight = 0
            if line.product_id and line.product_id.weight:
                weight += (line.product_id.weight * line.product_uom_qty)
            line.weight = weight

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update({'weight': self.weight})
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_weight = fields.Float(string="Weight", readonly=True, compute='_compute_total_weight')
    weight_unit = fields.Char(string="kg", readonly=True)

    def _compute_total_weight(self):
        for rec in self:
            total_weight = 0
            for line in rec.order_line:
                total_weight += line.weight or 0.0
            rec.total_weight = total_weight

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for order in self:
            order.picking_ids.write({'total_weight': self.total_weight})
        return result
