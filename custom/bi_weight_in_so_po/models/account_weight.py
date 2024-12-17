from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    weight = fields.Float(string="Weight(kg)", compute="_compute_weight")

    @api.onchange('product_id')
    def onchange_product_weight(self):
        for product in self:
            product.weight = product.product_id.weight

    def _compute_weight(self):
        for line in self:
            weight = 0
            if line.product_id and line.product_id.weight:
                weight += (line.product_id.weight * line.quantity)
            line.weight = weight


class AccountMove(models.Model):
    _inherit = "account.move"

    total_weight = fields.Float(string="Weight", readonly=True, compute="_compute_total_weight")
    weight_unit = fields.Char(string="kg", readonly=True)

    def _compute_total_weight(self):
        for rec in self:
            total_weight = 0
            for line in rec.invoice_line_ids:
                total_weight += line.weight or 0.0
            rec.total_weight = total_weight
