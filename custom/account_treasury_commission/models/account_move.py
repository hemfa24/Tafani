from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def js_assign_outstanding_line(self, line_id):
        res = super(AccountMove, self).js_assign_outstanding_line(line_id)
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'payment':
            if line_id:
                lines = self.env['account.move.line'].browse(line_id)
                if lines and lines[0].move_id.payment_id:
                    payment = lines[0].move_id.payment_id
                    payments_for_commission = payment.filtered(lambda pay: pay.is_create_payment_commission)
                    payments_for_commission.get_treasury_payment_commission(outstanging_inv_ids=self)
        return res

    def button_cancel(self):
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'sale_order':
            for invoice in self:
                if invoice.line_ids.sale_line_ids.order_id:
                    commission_lines = self.env['sale.commission.lines'].search([
                        ('order_id', '=', invoice.line_ids.sale_line_ids.order_id.id)
                    ])
                    commission_bill_ids = commission_lines.mapped('commission_bill_id')
                    if any(commission_bill_id.state != 'cancel' for commission_bill_id in commission_bill_ids):
                        raise ValidationError(_("Sorry, Not allowed to cancelled invoice until commission is billed."))
        return super(AccountMove, self).button_cancel()

    def button_draft(self):
        commission_configuration = self.env.user.company_id.commission_configuration
        # if commission_configuration == 'sale_order':
        if commission_configuration in ['sale_order', 'invoice']:
            for invoice in self:
                if invoice.line_ids.sale_line_ids.order_id:
                    commission_lines = self.env['sale.commission.lines'].search([
                        ('order_id', '=', invoice.line_ids.sale_line_ids.order_id.id)
                    ])
                    commission_bill_ids = commission_lines.mapped('commission_bill_id')
                    if any(commission_bill_id.state != 'cancel' for commission_bill_id in commission_bill_ids):
                        raise ValidationError(
                            _("Sorry, Not allowed to make Reset to draft invoice until commission is billed."))
        return super(AccountMove, self).button_draft()

#     _inherit = ['account.move', 'utm.mixin']
#
#     enrt_team_id = fields.Many2one(
#         'crm.team',
#         string='Sales Team'
#     )
#
#     @api.onchange("enrt_team_id")
#     def _onchange_enrt_team_id(self):
#         for rec in self:
#             rec.team_id = rec.enrt_team_id
#
#     @api.depends('invoice_user_id')
#     def _compute_team_id(self):
#         for move in self:
#             if move.enrt_team_id:
#                 move.team_id = move.enrt_team_id
#                 self -= move
#                 continue
#         return super(AccountMove, self)._compute_team_id()
