# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class accountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        res = super(accountPayment, self).action_post()
        if not self.is_internal_transfer:
            company_partner = self.env['res.company'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            print ("company_partner", company_partner)
            if company_partner and self.payment_type == 'outbound':
                print ("company_partner --- 1")
                """
                    Cash Management
                """
                print ("self.journal_id.type", self.journal_id.type)
                print ("\n\nn\n\n\n\n\n company_partner and self.payment_type", self.payment_type)
                if self.journal_id.type == 'cash':
                    if company_partner.treasury_journal_id:
                        payment_id = self.env['account.payment'].sudo().create({
                            'journal_id': company_partner.treasury_journal_id.id,
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'partner_id': self.env.company.partner_id.id,
                            'company_id': company_partner.id,
                            'amount': self.amount,
                            'date': self.date,
                            'ref': self.ref,
                            'manual_currency_rate_active': self.manual_currency_rate_active,
                            'manual_currency_rate': self.manual_currency_rate,
                            'currency_id': self.currency_id.id,
                        })
                        payment_id.onchange_partner()
                    else:
                        raise UserError(_(
                            'Please choose "Cash Treasury  Journal" for the company %s') % (
                                company_partner.name)
                            )
                else:
                    """
                        Bank Management
                    """
                    print ("Call HEREE", company_partner.treasury_bank_journal_id)
                    if company_partner.treasury_bank_journal_id:
                        print ("Call HEREE -----1")
                        payment_id = self.env['account.payment'].sudo().create({
                            'journal_id':
                                company_partner.treasury_bank_journal_id.id,
                            'payment_type': 'inbound',
                            'partner_type': 'customer',
                            'partner_id': self.env.company.partner_id.id,
                            'company_id': company_partner.id,
                            'amount': self.amount,
                            'date': self.date,
                            'ref': self.ref,
                            'manual_currency_rate_active': self.manual_currency_rate_active,
                            'manual_currency_rate': self.manual_currency_rate,
                            'currency_id': self.currency_id.id,
                        })
                        payment_id.onchange_partner()
                    else:
                        raise UserError(_(
                            'Please choose "Bank Treasury  Journal" for the company %s') % (
                                company_partner.name)
                            )
        return res
