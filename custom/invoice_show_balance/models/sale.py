# -*- coding: utf-8 -*-

from odoo import api, models, fields

class saleOrder(models.Model):
    _inherit= 'sale.order'
    
    @api.onchange('partner_id')
    def credit_debit_get(self):
        partner = self.partner_id
        if not partner:
            return
        else:
            partner = partner.ids

        tables, where_clause, where_params = self.env['account.move.line'].with_context(state='posted', company_id=self.env.company.id)._query_get()
        
        where_params = [tuple(partner)] + where_params
        if where_clause:
            where_clause = 'AND ' + where_clause
        self._cr.execute("""SELECT account_move_line.partner_id,  a.account_type, SUM(account_move_line.amount_residual)
                      FROM """ + tables + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                      AND account_move_line.partner_id IN %s
                      AND account_move_line.reconciled IS NOT TRUE
                      """ + where_clause + """
                      GROUP BY account_move_line.partner_id, a.account_type
                      """, where_params)
        treated = self.browse()


        for pid, type, val in self._cr.fetchall():
            if type == 'asset_receivable':
                self.credit = val
                
            elif type == 'liability_payable':
                self.debit = -val


    credit = fields.Float(
        string='Total Credit', help="Total amount this customer owes you.",)
    debit = fields.Float( string='Total Debit',
        help="Total amount you have to pay to this vendor.",)
    