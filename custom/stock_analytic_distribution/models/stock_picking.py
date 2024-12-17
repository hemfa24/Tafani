from odoo import models
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer()
    def apply_stock_analytic_distribution(self):
        if not self.analytic_distribution:
            raise ValidationError(_('Select Analytic Distribution'))
        for line in self.move_ids_without_package:
            line.analytic_distribution = self.analytic_distribution