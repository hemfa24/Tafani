
from odoo import api, fields, models,_
from odoo.exceptions import UserError


class DiscountConfigSettings(models.Model):
    _name = "sale.discount.settings"
    _description = 'Sale Discount Limit'
    _rec_name = "name"

    name = fields.Char('Discount Limit Name', required=True,readonly=True)
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], string='Discount Method')
    discount_amount = fields.Float('Discount Limit', default=0.0)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Type')
    active = fields.Boolean('Active', default=True)

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    def _action_confirm(self):
        res = super(SaleOrderInherit, self)._action_confirm()

        limit_obj =self.env['sale.discount.settings']
        if self.discount_type == 'global':
            if self.discount_amount > 0:
                git_global_val =limit_obj.search([('discount_type','=',self.discount_type),('discount_method','=',self.discount_method),('active','=',True)])
                if git_global_val and self.discount_amount > git_global_val.discount_amount:
                    raise UserError(
                        _("This Order it exceeded " + git_global_val.name))
        elif self.discount_type == 'line':
            for line in self.order_line:
                if line.discount_amount > 0:
                    git_global_val = limit_obj.search(
                        [('discount_type', '=', self.discount_type), ('discount_method', '=', line.discount_method),
                         ('active', '=', True)])
                    if git_global_val and line.discount_amount > git_global_val.discount_amount:
                        raise UserError(
                            _("This Order it exceeded " + git_global_val.name + " by line product : "  + str(line.product_id.name)))



        return res





