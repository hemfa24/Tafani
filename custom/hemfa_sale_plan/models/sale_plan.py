from odoo import api, fields, models


class salePlan(models.Model):
    _name = "sale.plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Sale Plan Name')
    line_ids = fields.One2many('sale.plan.line','plan_id')



class salePlanLine(models.Model):
    _name = "sale.plan.line"

    plan_id = fields.Many2one('sale.plan')

    customer_id = fields.Many2one('res.partner')
    sale_person_id  = fields.Many2one('res.users')
    lot_id = fields.Many2one('stock.lot')
    max_qty = fields.Integer()
    start_date = fields.Datetime()
    end_date = fields.Datetime()