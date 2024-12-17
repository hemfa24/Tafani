from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.constrains('partner_id','user_id')
    def check_sale_plan(self):
        for rec in self:
            rec.order_line.check_sale_plan()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('product_id','lot_id','product_uom_qty',)
    def check_sale_plan(self):
        """
        check sale plan restriction for lot 
        """
        # if not self.env.user.has_group('hemfa_sale_plan.group_sale_plan'):
        #     return
        plan_line_obj = self.env['sale.plan.line']
        for rec in self:
            if rec.lot_id:
                if rec.order_id.partner_id:
                    plan_lines = plan_line_obj.search([
                        ('lot_id','=',rec.lot_id.id),
                        ('customer_id','=',rec.order_id.partner_id.id)
                        ])
                    
                    for plan_line in plan_lines:
                        if rec.product_uom_qty > plan_line.max_qty:
                            if not plan_line.start_date or (rec.order_id.date_order >= plan_line.start_date and rec.order_id.date_order <= plan_line.end_date):
                                raise ValidationError(_("Customer (%s) Exceed Planned Max QTY (%s) for lot (%s) in Sale Plan (%s) .",rec.order_id.partner_id.name, plan_line.max_qty,rec.lot_id.name,plan_line.plan_id.name))
                
                if rec.order_id.user_id:
                    plan_lines = plan_line_obj.search([
                        ('lot_id','=',rec.lot_id.id),
                        ('sale_person_id','=',rec.order_id.user_id.id)
                        ])
                    
                    for plan_line in plan_lines:
                        if rec.product_uom_qty > plan_line.max_qty:
                            if not plan_line.start_date or (rec.order_id.date_order >= plan_line.start_date and rec.order_id.date_order <= plan_line.end_date):
                                raise ValidationError(_("Sales Person (%s) Exceed Planned Max QTY (%s) for lot (%s) in Sale Plan (%s) .",rec.order_id.user_id.name, plan_line.max_qty,rec.lot_id.name,plan_line.plan_id.name))
                






    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        copy=False,
        compute="_compute_lot_id",
        store=True,
        readonly=False,
    )

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id")
    def _compute_lot_id(self):
        for sol in self:
            if sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False
