# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class AccountAccountType(models.Model):
    _inherit = "account.account"
    _description = "Account Type"

    close_method = fields.Selection([('none', 'None'),
                                     ('balance', 'Balance'),
                                     #('detail', 'Detail'),
                                     ('unreconciled', 'Unreconciled')],
                                     'Deferral Method', default='none',
                                     help="""Set here the method that will be used to generate the end of year journal entries for all the accounts of this type.""")

    coa_account_type = fields.Selection([
        ('annual_equity_type', 'Annual Equity Type'),
        ('pl_equity_type', 'Prior type'),
        ('earning', 'Current Year Earning Type')],
        string='COA Equity Method'
    )


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.depends('invoice_date', 'date')
    def _compute_get_period(self):
        for record in self:
            if record.invoice_date or record.date:
                today = record.invoice_date or record.date
                period_ids = self.env['account.period'].search([('date_start','<=',today), ('date_stop','>=',today)], limit=1)
                record.period_id = period_ids

    period_id = fields.Many2one('account.period', string='Force Period',
                                store=True,
                                readonly=True, compute='_compute_get_period',
                                help="Keep empty to use the period of the validation(invoice) date.",
                                states={'draft': [('readonly', False)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year',
                                    related='period_id.fiscalyear_id', store=True)


class AccountJournal(models.Model):
    _inherit = "account.journal"
    _description = "Journal"

    type = fields.Selection(selection_add=[
        ('situation', 'Opening/Closing Situation')
    ], ondelete={'situation': 'cascade'},
        help="Select 'Sale' for customer invoices journals.\n"\
        "Select 'Purchase' for vendor bills journals.\n"\
        "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
        "Select 'General' for miscellaneous operations journals.\n"\
        "Select 'Opening/Closing Situation' for entries generated for new fiscal years.")

    centralisation = fields.Boolean('Centralized Counterpart', help="Check this box to determine that each entry of this journal won't create a new counterpart but will share the same counterpart. This is used in fiscal year closing.")
    entry_posted = fields.Boolean('Autopost Created Moves', help='Check this box to automatically post entries of this journal. Note that legally, some entries may be automatically posted when the source document is validated (Invoices), whatever the status of this field.')

class AccountMove(models.Model):
    _inherit = "account.move"


    @api.onchange('date')
    def _onchange_date(self):
        '''On the form view, a change on the date will trigger onchange() on account.move
        but not on account.move.line even the date field is related to account.move.
        Then, trigger the _onchange_amount_currency manually.
        '''
        if self.date:
            period_id = self.env['account.period'].search([('date_start','<=',self.date), ('date_stop','>=',self.date)], limit=1)
            self.period_id = period_id.id
        # self.line_ids._onchange_amount_currency()

    @api.constrains('date', 'period_id')
    def check_period(self):
        for record in self:
            if record.period_id.state == 'done':
                raise UserError(_('You can not create journal entries in a closed period %s') % (record.period_id.name))

    @api.constrains('fiscalyear_id')
    def check_fiscalyear(self):
        for record in self:
            if record.fiscalyear_id.state == 'done':
                raise UserError(_('%s is already closed') % (record.fiscalyear_id.name))

    @api.model_create_multi
    def create(self, vals_list):
        context = dict(self._context or {})
        for vals in vals_list:
            context['period_id'] = vals['period_id'] if 'period_id' in vals else self._compute_get_period()
            context['check_move_validity'] = False
            context['partner_id'] = vals.get('partner_id')
        move = super(AccountMove, self.with_context(context)).create(vals_list)
        container = {'records': self}
        move_container = {'records': move, 'self': self}
        move._check_balanced(move_container)
        return move

    def _centralise(self, mode):
        assert mode in ('debit', 'credit'), 'Invalid Mode' #to prevent sql injection
        account_move_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        currency_obj = self.env['res.currency']
        context = self._context.copy()
        #print("context", context)
        income_account_type = ['income', 'income_other']
        expance_account_type = ['expense', 'expense_depreciation', 'expense_direct_cost']

        #Prview year trasnfer Balanace
        account_type = ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']
        

        for move in self:
            t_credit = 0.0
            t_debit = 0.0

            start_date = move.period_id.fiscalyear_id.date_start - relativedelta(years=1)
            date_stop = move.period_id.fiscalyear_id.date_stop - relativedelta(years=1)


            account_ids = account_obj.sudo().search([
                ('account_type', 'in', account_type)
            ])


            annual_equity_type_id = account_obj.search([
                ('coa_account_type', '=', 'annual_equity_type')
            ])

            pl_equity_type_id = account_obj.search([
                ('coa_account_type', '=', 'pl_equity_type')
            ])
            
            t_move_lines = account_move_line_obj.sudo().search([
                ('account_id', 'in', account_ids.ids),
                ('date', '>=', start_date),
                ('date', '<=', date_stop)
            ])
            Total_Balance = sum(
                t_move_lines.mapped("credit")
                ) - sum(
                    t_move_lines.mapped("debit")
                )
            domain = [
                    ('date', '>=', start_date),
                    ('date', '<=', date_stop)
                ]
            print("Total_Balance", Total_Balance)
            if mode=='credit':
                print("\n\n ******  -888 - IF --- - - - Credit  - -- - -- -", start_date, date_stop)
              

                expance_account = account_obj.sudo().search([('account_type', 'in', expance_account_type)])
                move_lines = account_move_line_obj.sudo().search([
                    ('account_id', 'in', expance_account.ids),
                    ('date', '>=', start_date),
                    ('date', '<=', date_stop)
                ])

                t_debit = sum(move_lines.mapped("debit")) - sum(move_lines.mapped("credit"))
                mode2 = 'debit'
                if Total_Balance > 0:
                    account_id = pl_equity_type_id
                else:
                    account_id = annual_equity_type_id

            else:
                print("\n\n ******  - - --- - - - ELSSDEBIT   - -- - -- -")
                mode2 = 'credit'
                income_account = account_obj.sudo().search([('account_type', 'in', income_account_type)])

                move_lines = account_move_line_obj.sudo().search(domain + [('account_id', 'in', income_account.ids)])
                t_credit = sum(move_lines.mapped("debit")) - sum(move_lines.mapped("credit"))
                if Total_Balance > 0:
                    account_id = annual_equity_type_id
                else:
                    account_id = pl_equity_type_id
    
            # find the first line of this move with the current mode
            # or create it if it doesn't exist
            print("\n\n  ***  Credit And Debit", t_credit, t_debit)
            if t_credit != 0.0:
                if t_credit > 0:
                    print ("IF CALL ")
                    t_credit += Total_Balance
                else:
                    t_credit -= Total_Balance
                    print ("CALL ELSE")
            if t_debit != 0.0:
                if t_debit > 0:
                    print ("IF CALL ")
                    t_debit += Total_Balance
                else:
                    t_debit -= Total_Balance

            print("\n\n  *** AFTER Call Credit And Debit", t_credit, t_debit)
            #STOP
            self.env.cr.execute('select id from account_move_line where move_id=%s and centralisation=%s limit 1', (move.id, mode))
            res = self.env.cr.fetchone()
            if res:
                line_id = res[0]
            else:
                context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
                line_id = account_move_line_obj.with_context(context).create({
                    'name': _(mode.capitalize()+' Centralisation'),
                    'centralisation': mode,
                    'partner_id': False,
                    'account_id': account_id.id,
                    'move_id': move.id,
                    'journal_id': move.journal_id.id,
                    'period_id': move.period_id.id,
                    'date': move.period_id.date_stop,
                    'debit': 0.0,
                    'credit': 0.0,
                    'parent_state': 'posted'
                })
                line_id = line_id.id
                self.env.cr.execute('update account_move_line set credit=%s, debit=%s where id=%s', (abs(t_credit), abs(t_debit), line_id))
                if mode == 'credit':
                    self.env.cr.execute('update account_move_line set balance=%s where id=%s', (t_debit, line_id))
                else:
                    self.env.cr.execute('update account_move_line set balance=%s where id=%s', (t_credit, line_id))
        return True

    def _centralise_currency(self):
        account_move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        context = self._context.copy()
        for move in self:
            self.env.cr.execute("select currency_id, sum(amount_currency) as amount_currency from account_move_line where move_id = %s and currency_id is not null group by currency_id", (move.id,))
            currency_result = self.env.cr.dictfetchall()
            if currency_result:
                for row in currency_result:
                    currency_id = currency_obj.browse(row.get('currency_id'))
                    if not currency_id.is_zero(row.get('amount_currency')):
                        amount_currency = row.get('amount_currency') * -1
                        account_id = amount_currency > 0 and move.journal_id.company_id.account_journal_payment_debit_account_id.id or move.journal_id.company_id.account_journal_payment_credit_account_id.id
                        self.env.cr.execute('select id from account_move_line where move_id=%s and centralisation=\'currency\' and currency_id = %s limit 1', (move.id, row['currency_id']))
                        res = self.env.cr.fetchone()
                        if res:
                            self.env.cr.execute('update account_move_line set amount_currency=%s , account_id=%s where id=%s', (amount_currency, account_id, res[0]))
                            self.env.invalidate_all()
                        else:
                            context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
                            line_id = account_move_line_obj.create({
                                'name': _('Currency Adjustment'),
                                'centralisation': 'currency',
                                'partner_id': False,
                                'account_id': account_id,
                                'move_id': move.id,
                                'journal_id': move.journal_id.id,
                                'period_id': move.period_id.id,
                                'date': move.period_id.date_stop,
                                'debit': 0.0,
                                'credit': 0.0,
                                'currency_id': row['currency_id'],
                                'amount_currency': amount_currency,
                            })
        return True

    #
    # Validate a balanced move. If it is a centralised journal, create a move.
    #
    def validate(self):
        valid_moves = [] #Maintains a list of moves which can be responsible to create analytic entries
        obj_move_line = self.env['account.move.line']
        for move in self:
            journal = move.journal_id
            amount = 0
            line_ids = []
            line_draft_ids = []
            company_id = None
            # makes sure we don't use outdated period
            obj_move_line._update_journal_check(journal.id, move.period_id.id)
            for line in move.line_ids:
                amount += line.debit - line.credit
                line_ids.append(line.id)
                if line.parent_state == 'draft':
                    line_draft_ids.append(line.id)

                if not company_id:
                    company_id = line.account_id.company_id.id
                if not company_id == line.account_id.company_id.id:
                    raise UserError(_("Cannot create moves for different companies."))

                if line.account_id.currency_id and line.currency_id:
                    if line.account_id.currency_id.id != line.currency_id.id and (line.account_id.currency_id.id != line.account_id.company_id.currency_id.id):
                        raise UserError(_("""Couldn't create move with currency different from the secondary currency of the account "%s - %s". Clear the secondary currency field of the account definition if you want to accept all currencies.""") % (line.account_id.code, line.account_id.name))
            if abs(amount) < 10 ** -5:
                # If the move is balanced
                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move.id)
                # Check whether the move lines are confirmed
                if not line_draft_ids:
                    continue
                # Update the move lines (set them as valid)
                move_line_ids = obj_move_line.browse(line_draft_ids)
                move_line_ids.write({'parent_state': 'posted'})

                account = {}
                account2 = {}

                if journal.type in ('purchase','sale'):
                    for line in move.line_id:
                        code = amount = 0
                        key = (line.account_id.id, line.tax_code_id.id)
                        if key in account2:
                            code = account2[key][0]
                            amount = account2[key][1] * (line.debit + line.credit)
                        elif line.account_id.id in account:
                            code = account[line.account_id.id][0]
                            amount = account[line.account_id.id][1] * (line.debit + line.credit)
                        if (code or amount) and not (line.tax_code_id or line.tax_amount):
                            line.write({
                                'tax_code_id': code,
                                'tax_amount': amount
                            })
            elif journal.centralisation:
                # If the move is not balanced, it must be centralised...

                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move.id)
                #
                # Update the move lines (set them as valid)
                #
                move._centralise('debit')
                move._centralise('credit')
                move_line_ids = obj_move_line.browse(line_draft_ids)
                move_line_ids.write({'parent_state': 'posted'})
            else:
                # We can't validate it (it's unbalanced)
                # Setting the lines as draft
                not_draft_line_ids = list(set(line_ids) - set(line_draft_ids))
                if not_draft_line_ids:
                    draft_line_ids = obj_move_line.browse(not_draft_line_ids)
                    draft_line_ids.write({'parent_state': 'posted'})
        # Create analytic lines for the valid moves
        valid_moves_ids = self.env['account.move'].browse(valid_moves)
        for move in valid_moves_ids:
            move.line_ids._create_analytic_lines()
        valid_moves = [move.id for move in valid_moves_ids]
        return len(valid_moves) > 0 and valid_moves or False

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = "Journal Items"

    currency_id = fields.Many2one('res.currency', string='Currency', required=False)
    period_id = fields.Many2one('account.period', string='Period', ondelete='restrict', readonly=True,
                                         related='move_id.period_id', store=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year',related='period_id.fiscalyear_id', store=True)
    centralisation = fields.Selection([('normal','Normal'),('credit','Credit Centralisation'),('debit','Debit Centralisation'),('currency','Currency Adjustment')], 'Centralisation', default='normal')

    def _update_journal_check(self, journal_id, period_id):
        journal_obj = self.env['account.journal']
        period_obj = self.env['account.period']
        jour_period_obj = self.env['account.journal.period']
        self.env.cr.execute('SELECT state FROM account_journal_period WHERE journal_id = %s AND period_id = %s', (journal_id, period_id))
        result = self.env.cr.fetchall()
        journal = journal_obj.browse(journal_id)
        period = period_obj.browse(period_id)
        for (state,) in result:
            if state == 'done':
                raise UserError(_('You can not add/modify entries in a closed period %s of journal %s.') % (period.name, journal.name))
        if not result:
            jour_period_obj.create({
                'name': (journal.code or journal.name)+':'+(period.name or ''),
                'journal_id': journal.id,
                'period_id': period.id
            })
        return True

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')
        fiscalyear_obj = self.env['account.fiscalyear']
        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = safe_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from'])]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('move_id.state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]

        if 'company_ids' in context:
            domain += [('company_id', 'in', context['company_ids'])]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]
 
        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]
 
        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]
 
        if context.get('analytic_tag_ids'):
            domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]
 
        if context.get('analytic_account_ids'):
            domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]
 
        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]
 
        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        if not context.get('fiscalyear'):
            if context.get('all_fiscalyear'):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search([])
                domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]
            else:
                fiscalyear_ids = fiscalyear_obj.search([('state', '=', 'draft')])
                domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = context.get('fiscalyear')
            domain += [('fiscalyear_id', 'in', fiscalyear_ids.ids), ('move_id.state', '=', 'draft')]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            query = self._where_calc(domain)
            # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params


    def convert_to_period(self):
        context = dict(self._context or {})
        period_obj = self.env['account.period']
        #check if the period_id changed in the context from client side
        if context.get('period_id', False):
            period_id = context.get('period_id')
            if type(period_id) == str:
                period_ids = period_obj.search([('name', 'ilike', period_id)])
                context = dict(context, period_id=period_ids and period_ids[0] or False)
        return context

