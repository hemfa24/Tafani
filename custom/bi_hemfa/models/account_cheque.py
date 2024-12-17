# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class accountCheque(models.Model):
    _inherit = "account.cheque"

    def write(self, vals):
        result = super(accountCheque, self).write(vals)
        for rec in self:
            if vals.get('status') and rec.status == 'registered':
                print ("\n\n\n\nn\n\n ALLll ")
                company_partner = self.env['res.company'].sudo().search([('partner_id', '=', self.payee_user_id.id)], limit=1)
                if company_partner:
                    # journal = self.env['account.journal'].search([('type', '=', self.journal_id.type),
                    # 
                    #                                               ('company_id', '=', company_partner.id)], limit=1)
                    print ("\n\\n- - -- -company_partner", company_partner, company_partner.in_credit_account_id, company_partner.in_debit_account_id)
                    if not company_partner.treasury_cheque_journal_id:
                        raise UserError(_(
                            'Please choose "Cheque Treasury  Journal" for the company %s') % (
                            company_partner.name)
                        )
                    # if not company_partner.treasury_credit_account_id or not company_partner.treasury_debit_account_id:
                    #     raise UserError(_(
                    #         'Please choose "Cheque Credit and Debit Accounts" for the company %s') % (
                    #         company_partner.name)
                    #     )id
                    cheque_id = False
                    company_second_partner = self.env['res.partner'].sudo().search([('id', '=', self.company_id.partner_id.id),('company_id', '=', company_partner.id)], limit=1)
                    print ("\n\n= = = == == = = =  ", company_second_partner)
                    print ("self.env.company.partner_idself.env.company.partner_id", self.company_id.partner_id.name, self.company_id.partner_id.property_account_receivable_id.code)
                    print ("Second COmpany Partner ",  company_partner.name, company_partner.partner_id.property_account_receivable_id, company_partner.in_debit_account_id.code)
                    
                    # Another Company DataBase
                    
                    PropertyObj = self.env['ir.property'].sudo()
                    prop_values = 'res.partner,%s' % self.company_id.partner_id.id
                    


                    #STOP
                    if self.account_cheque_type == 'outgoing':

                        property_account_receivable_id = False
                        Property_id = PropertyObj.search([
                            ('res_id', '=', prop_values),
                            ('name', '=', 'property_account_receivable_id'),
                            ('company_id', '=', company_partner.id),
                        ])

                        if Property_id.value_reference:
                            value_account_id = int(Property_id.value_reference.split(',')[1])
                            property_account_receivable_id = self.env['account.account'].sudo().search([
                                ('id', '=', value_account_id)
                            ], limit=1)
                        print ("property_account_receivable_id", property_account_receivable_id.code)
                        cheque_id = self.env['account.cheque'].sudo().with_context(inter_company=True).create({
                            'name': self.name,
                            'cheque_number': self.cheque_book_line_id.page,
                            'amount': self.amount,
                            'account_cheque_type': 'incoming',
                            'ref': self.ref,
                            'credit_account_id':
                                property_account_receivable_id.id,
                            'debit_account_id':
                                company_partner.in_debit_account_id.id if company_partner.in_debit_account_id else False,
                            'cheque_receive_date': self.cheque_date,
                            'payee_user_id': self.env.company.partner_id.id,
                            'company_id': company_partner.id,
                            'journal_id':
                                company_partner.treasury_cheque_journal_id.id
                        })
                    elif self.account_cheque_type == 'incoming':
                        print ("CALll - - --- -- - - - -- - - -- - - - - --")
                        property_account_payable_id = False
                        Property_id = PropertyObj.search([
                            ('res_id', '=', prop_values),
                            ('name', '=', 'property_account_payable_id'),
                            ('company_id', '=', company_partner.id),
                        ])

                        if Property_id.value_reference:
                            value_account_id = int(Property_id.value_reference.split(',')[1])
                            property_account_payable_id = self.env['account.account'].sudo().search([
                                ('id', '=', value_account_id)
                            ], limit=1)

                        cheque_id = self.env['account.cheque'].sudo().create({
                            'name': self.name,
                            'cheque_number': self.cheque_book_line_id.page,
                            'amount': self.amount,
                            'ref': self.ref,
                            'account_cheque_type': 'outgoing',
                            'credit_account_id':
                                company_partner.out_credit_account_id.id if company_partner.out_credit_account_id else False,
                            'debit_account_id': property_account_payable_id.id,
                            'cheque_receive_date': self.cheque_date,
                            'payee_user_id': self.env.company.partner_id.id,
                            'company_id': company_partner.id,
                            'journal_id':
                                company_partner.treasury_cheque_journal_id.id
                        })
                    if cheque_id:
                        cheque_id.count_account_invoice()
                    #STOP 
                # else:
                #     if self.account_cheque_type == 'outgoing':
                #         self.env['account.cheque'].create({
                #             'name': self.name,
                #             'cheque_number': self.cheque_book_line_id.page,
                #             'amount': self.amount,
                #             'account_cheque_type': 'incoming',
                #             'cheque_receive_date': self.cheque_date,
                #             'payee_user_id': self.env.company.partner_id.id,
                #         })
                #     elif self.account_cheque_type == 'incoming':
                #         self.env['account.cheque'].create({
                #             'name': self.name,
                #             'cheque_number': self.cheque_book_line_id.page,
                #             'amount': self.amount,
                #             'account_cheque_type': 'outgoing',
                #             'cheque_receive_date': self.cheque_date,
                #             'payee_user_id': self.env.company.partner_id.id,
                #         })
        # res = super(accountCheque, self).set_to_submit()
        return result

