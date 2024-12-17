import datetime

from odoo import models, fields, api, _
import logging

from odoo.exceptions import AccessError, UserError, ValidationError

logger = logging.getLogger(__name__)


class WiCloseSession(models.TransientModel):
    _name = "wi.close.session"
    session_id = fields.Many2one(
        "pos.session",
        string="pos session",
        readonly=True,
    )
    order_count = fields.Integer(related="session_id.order_count")
    opening_notes = fields.Text(related="session_id.opening_notes")
    total_payments_amount = fields.Float(related="session_id.total_payments_amount")
    payment_method_ids = fields.Many2many(related="session_id.payment_method_ids")
    currency_id = fields.Many2one(related="session_id.currency_id")
    currency_id = fields.Many2one(related="session_id.currency_id")
    cash_real_transaction = fields.Monetary(related="session_id.cash_real_transaction")
    cash_register_balance_end_real = fields.Monetary(
        related="session_id.cash_register_balance_end_real"
    )
    statement_line_ids = fields.One2many(related="session_id.statement_line_ids")
    bank_payment_ids = fields.One2many(related="session_id.bank_payment_ids")
    order_ids = fields.One2many(related="session_id.order_ids")
    close_custom = fields.One2many(related="session_id.close_custom")

    def save_date(self):
        for rec in self:
            cashcount = 0.0
            for o in rec.close_custom:
                if o.payment_method.name == "Cash":
                    cashcount += o.custom_counted
            # self.session_id.post_closing_cash_details(cashcount)
            # rec.session_id.update_closing_control_state_session("notes")
            # rec.session_id.close_session_from_ui(bank_payment_method_diff_pairs=None)
            rec.session_id.action_pos_session_closing_control()

    def generate_report_custom(self):
        data = {'date_start': False, 'date_stop': False, 'config_ids': self.session_id.config_id.ids, 'session_ids': self.session_id.ids}
        return self.env.ref('point_of_sale.sale_details_report').report_action([], data=data)



    @api.onchange("session_id")
    def _onchange_close_date_set(self):
        for rec in self:
            print("hi1")
            rec.session_id.close_custom = False
            orders = self.order_ids.filtered(
                lambda o: o.state == "paid"
                or o.state == "done"
                or o.state == "invoiced"
            )
            obj_payment = (
                self.env["pos.payment"]
                .sudo()
                .search([("session_id", "=", rec.session_id.id)])
            )
            print("hi2")
            print(obj_payment)
            for pay_id in rec.payment_method_ids:
                yy = sum(
                    orders.payment_ids.filtered(
                        lambda p: p.payment_method_id == pay_id
                    ).mapped("amount")
                )
                count = 0.0
                for record in obj_payment:
                    if record.payment_method_id.name == pay_id.name:
                        count += record.amount

                print(pay_id.id)

                print(yy)
                print(count)
                self.env["custom.session.close.data"].sudo().create(
                    {
                        "session_id": rec.session_id.id,
                        "payment_method": pay_id.id,
                        "custom_expected": count,
                        "custom_counted": 0.0,
                        "custom_difference": 0.0,
                    }
                )
            print("hi3")
        print("hi4")
