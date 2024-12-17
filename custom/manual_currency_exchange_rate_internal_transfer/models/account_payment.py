# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # Fully Override
    def _create_paired_internal_transfer_payment(self):
        ''' When an internal transfer is posted, a paired payment is created
        with opposite payment_type and swapped journal_id & destination_journal_id.
        Both payments liquidity transfer lines are then reconciled.
        '''
        for payment in self:
            paired_payment = payment.copy({
                'journal_id': payment.destination_journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                'move_id': None,
                'ref': payment.ref,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
                'partner_id': self.env.company.partner_id.id,
                'company_id': self.env.company.id,
                'bank_reference': payment.bank_reference,
                'cheque_reference': payment.cheque_reference,
                'currency_id': payment.currency_id.id,
                'analytic_distribution': payment.analytic_distribution,
                'manual_currency_rate': payment.manual_currency_rate,  # Added 7 Mar 24
                'manual_currency_rate_active': payment.manual_currency_rate_active,  # Added 7 Mar 24
            })
            """
                3 June
                @required only draft JE
            """
            # paired_payment.move_id._post(soft=False)
            payment.paired_internal_transfer_payment_id = paired_payment

            body = _(
                "This payment has been created from %s",
                payment._get_html_link(),
            )
            paired_payment.message_post(body=body)
            body = _(
                "A second payment has been created: %s",
                paired_payment._get_html_link(),
            )
            payment.message_post(body=body)
            """
                3 June
                @required only draft JE // becuase of not posted JE 
            """
            # lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
            #     lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            # lines.reconcile()
