# -*- coding: utf-8 -*-

from odoo import api, models, fields

class accountMove(models.Model):
    _inherit= 'account.move'

    # @api.depends('move_type', 'line_ids.amount_residual')
    # def _compute_payments_widget_reconciled_info(self):
    #     res = super(accountMove,self)._compute_payments_widget_reconciled_info()
        
    #     for rec in self:
    #         rec.credit_debit_get()
            
    #     return res

    # @api.model
    # def create(self,vals):
    #     res = super(accountMove,self).create(vals)

    #     if res.partner_id:
    #         res.credit_debit_get()
    #     return res

    
    # def action_post(self):
    #     res = super(accountMove,self).action_post()
    #     for rec in self:
    #         rec.credit_debit_get()
    #     return res

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     res = super(accountMove,self)._onchange_partner_id()
    #     for rec in self:
    #         rec.credit_debit_get()
    #     return res

    @api.depends('partner_id','state','invoice_payments_widget')
    def _credit_debit_get(self):
        self.credit = 0
        self.debit = 0
        partner = self.partner_id
        if not partner:
            return
        else:
            partner = partner.ids

        tables, where_clause, where_params = self.env['account.move.line'].with_context(state='posted', company_id=self.env.company.id)._query_get()
        
        where_params = [tuple(partner)] + where_params
        if where_clause:
            where_clause = 'AND ' + where_clause
        print(where_clause)
        print(where_params)
        result=self._cr.execute("""SELECT account_move_line.partner_id, a.account_type, SUM(account_move_line.amount_residual)
                      FROM """ + tables + """
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                      AND account_move_line.partner_id IN %s
                      AND account_move_line.reconciled IS NOT TRUE
                      """ + where_clause + """
                      GROUP BY account_move_line.partner_id, a.account_type
                      """, where_params)
        treated = self.browse()
        print("result_________________________________________________________________________________")
        print(result)
        print(treated)
        for pid, account_type, val in self._cr.fetchall():
            print(val)
            if account_type == 'asset_receivable':
                self.credit = val
                
            elif account_type == 'liability_payable':
                self.debit = -val


    credit = fields.Float(compute="_credit_debit_get",
        string='Total Credit', help="Total amount this customer owes you.",)
    debit = fields.Float(compute="_credit_debit_get", string='Total Debit',
        help="Total amount you have to pay to this vendor.",)