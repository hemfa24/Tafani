# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
# import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import UserError
import json
from odoo.tools import float_is_zero, float_compare

class AccountCheque(models.Model):
	_name = "account.cheque"
	_order = 'id desc'
	_description = "account.cheque"

	sequence = fields.Char(string='Sequence', readonly=True, copy=True, index=True)
	name = fields.Char(string="Name", required="1", copy=False)
	bank_account_id = fields.Many2one('account.account','Bank Account')
	account_cheque_type = fields.Selection([('incoming','Incoming'),('outgoing','Outgoing')],string="Cheque Type")
	cheque_number = fields.Char(string="Cheque Number", required=True, copy=False)
	re_amount = fields.Float(string="Remaining Amount", compute='_get_outstanding_info',)
	
	amount = fields.Float(string="Amount",required=True)
	cheque_date = fields.Date(string="Cheque Date",default=datetime.now().date())
	cheque_given_date = fields.Date(string="Cheque Given Date")
	cheque_receive_date = fields.Date(string="Cheque Receive Date")
	cheque_return_date = fields.Date(string="Cheque Return Date")
	payee_user_id = fields.Many2one('res.partner',string="Payee", required="1")
	payee_type = fields.Selection([('partner','Partner'),('employee','Employee')],default='partner')
	employee_id = fields.Many2one('hr.employee',string="Employee",copy=False)

	@api.onchange('payee_type','employee_id')
	def onchange_set_employee_partner(self):
		for rec in self:
			if rec.payee_type == 'employee':
				if not rec.employee_id:
					rec.payee_user_id = False
				if rec.employee_id:
					rec.payee_user_id = rec.employee_id.user_id.partner_id.id if rec.employee_id.user_id else rec.employee_id.address_home_id.id
  

	credit_account_id = fields.Many2one('account.account', string="Credit Account")
	debit_account_id = fields.Many2one('account.account', string="Debit Account")
	comment = fields.Text(string="Comment")
	attchment_ids = fields.One2many('ir.attachment','account_cheque_id',string="Attachment")
	status = fields.Selection([('draft','Draft'),('registered','Registered'),('bounced','Bounced'),('return','Returned'),('cashed','Done'),('cancel','Cancel')],string="Status",default="draft",copy=False, index=True)
	
	status1 = fields.Selection([('draft','Draft'),('registered','Registered'),('bounced','Bounced'),('return','Returned'),('deposited','Deposited'),('transfered','Transfered'),('cashed','Done'),('cancel','Cancel')],string="Status",default="draft",copy=False, index=True)

	state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string="State", default="draft", copy=False,
							 index=True, )

	journal_id = fields.Many2one('account.journal', 'Bank', domain=[('type','=','bank')])
	journal_type = fields.Selection(related="journal_id.type")
	company_id = fields.Many2one('res.company',string="Company",required=True)
	journal_items_count = fields.Integer(compute='_active_journal_items', string="Journal Items")
	invoice_ids = fields.Many2many('account.move','account_move_invoice_payee_rel',
	#  compute="_count_account_invoice",
	  string="Invoices",copy=False)
	attachment_count = fields.Integer('Attachments', compute='_get_attachment_count')
	in_count = fields.Boolean('Incoice', compute='_get_in_count')
	is_partial = fields.Boolean(string='Not reconciled')

	cheque_operation_ids = fields.One2many('account.cheque.operation', 'account_cheque_id')
	cheque_book_id = fields.Many2one('cheque.book', 'Cheque Book', copy=False)
	cheque_book_line_id = fields.Many2one('cheque.book.line', 'Cheque Page', copy=False)
	outgoing_residual = fields.Float('Remaining Amount')
	partner_type = fields.Selection([
		('customer', 'Customer'),
		('supplier', 'Vendor'),
		('employee', 'Employees'),
	], default='customer', tracking=True, required=True)
	is_no_accounting_effect = fields.Boolean('No Accounting Effect')
	paid_ids = fields.Many2many('account.move','account_move_invoice_paid_rel',copy=False,help="reconciled moves ")
	
	checked_invoices_ids = fields.Many2many('account.move','account_move_invoice_checked_rel',copy=False,help="reconciled moves ")
	

	@api.onchange('payee_user_id')
	def count_account_invoice(self):
		invoice_list = []
		self.invoice_ids = None
		print ("self.payee_user_id", self.payee_user_id, self.payee_user_id.company_id)
		if self.payee_user_id and not self._context.get('inter_company'):
			if self._context.get('default_account_cheque_type') == 'incoming' or self.account_cheque_type == 'incoming':
				print ("Ca........ ELLE 866666", self.payee_user_id.property_account_receivable_id.code)
				self.credit_account_id = self.payee_user_id.property_account_receivable_id.id if self.payee_user_id.property_account_receivable_id else False
			else:
				print ("Ca........ ELLE 888")
				self.debit_account_id = self.payee_user_id.property_account_payable_id.id if self.payee_user_id.property_account_payable_id else False
			

		for invoice in self.payee_user_id.invoice_ids.filtered(lambda mv: mv.state != 'draft'):
			invoice.check = False
			if invoice.state != 'cancel':
				if invoice.payment_state != 'paid':
					if self.account_cheque_type == 'incoming':
						if invoice.move_type == 'out_invoice':
							invoice_list.append(invoice.id)
							if invoice_list:
								self.invoice_ids = [(6, 0, invoice_list)]
					if self.account_cheque_type == 'outgoing':
						if invoice.move_type == 'in_invoice':
							invoice_list.append(invoice.id)
							if invoice_list:
								self.invoice_ids = [(6, 0, invoice_list)]
			if invoice.has_reconciled_entries == True:
				if self.account_cheque_type == 'incoming' and self.status1 == 'cancel':
					invoice.button_cancel()
				if self.account_cheque_type == 'outgoing' and self.status == 'cancel':
					invoice.button_cancel()

		self.re_compute_invoice()			
		
	def re_compute_invoice(self):
		for invoice in self.invoice_ids:
			
			invoice = invoice._origin
			
			# invoice_search = self.env['account.move'].browse(invoice.id)
			invoice.payment_state_cheque = invoice.payment_state
			invoice.amount_residual_cheque = invoice.amount_residual



	@api.model
	def create(self, vals):
		res = super(AccountCheque, self).create(vals)
		
		for rec in res:
			
			for invoice in rec.checked_invoices_ids:
				for line in rec.invoice_ids:
					if invoice.id == line.id:
						line.check = True
	
		
		return res


	@api.onchange('invoice_ids','invoice_ids.check')
	def save_checked_invoices(self):
		for rec in self:
			rec.checked_invoices_ids = rec.invoice_ids.filtered(lambda mv: mv.check == True).ids
				
			


	def write(self, vals):
		res = super(AccountCheque, self).write(vals)

		if vals.get('status1', False) or vals.get('status', False):
			for rec in self:
				rec.active_get_line_state()
		return res

	@api.depends('status1', 'status')
	def active_get_line_state(self):
		for rec in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', rec.id)])
			journal_item_ids.get_line_state()

	@api.model
	def default_get(self, flds): 
		result = super(AccountCheque, self).default_get(flds)
		res = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
		# user_company_id = self.env.user.company_id
		user_company_id = self.env.company
		if self._context.get('default_account_cheque_type') == 'incoming':
			result['credit_account_id'] = user_company_id.in_credit_account_id.id
			result['debit_account_id'] = user_company_id.in_debit_account_id.id
			result['journal_id'] = self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id
			result['company_id'] = user_company_id.id
		else:
			result['credit_account_id'] = user_company_id.out_credit_account_id.id
			result['debit_account_id'] = user_company_id.out_debit_account_id.id
			result['journal_id'] = self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id
			result['company_id'] = user_company_id.id
		return result

	@api.onchange('amount', 'invoice_ids')
	def onchange_amount_set_outgoing_residual(self):
		for rec in self:
			if rec.account_cheque_type == 'outgoing':
				rec.outgoing_residual = 0
				invoice_due_total = 0
				for line in rec.invoice_ids:
					if line.check:
						invoice_due_total += line.amount_residual
				rec.outgoing_residual = invoice_due_total - rec.amount

	def action_incoming_cashed(self):
		if self.is_no_accounting_effect:
			self.no_accounting_effect_state('cashed')
			return
		for rec in self:
			# account_cheque = self.env['account.cheque'].browse(rec.id)
			account_move_obj = self.env['account.move']
			move_lines = []
			# if account_cheque.re_amount:
			if not self.env.user.company_id.deposite_account_id.id:
				raise UserError(("Sorry Please First Set Deposit account in Accounting Setting."))
			vals = {
				'date': rec.cheque_date,
				'journal_id': rec.journal_id.id,
				'company_id': rec.company_id.id,
				'state': 'draft',
				'ref': rec.cheque_number + '- ' + 'Cashed',
				'account_cheque_id': rec.id,
				
			}
			account_move = account_move_obj.create(vals)
			debit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': rec.journal_id.default_account_id.id,
				# 'debit' : account_cheque.re_amount,
				'debit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, debit_vals))
			credit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': self.company_id.deposite_account_id.id,
				# 'credit' : account_cheque.re_amount,
				'credit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, credit_vals))
			account_move.write({'line_ids': move_lines})

			account_move._post(soft=False)

			cheque_move = self.env['account.move'].search([('is_move_to_reconcile','=',True),('state','=','posted'),('account_cheque_id','=',rec.id)])
			dest_line = cheque_move.line_ids.filtered(lambda mv: mv.account_id.id == rec.credit_account_id.id)
			
			ids = []
			for line in rec.invoice_ids.filtered(lambda inv: inv.check == True):
				ids.append(line.id)
				
				line.js_assign_outstanding_line(dest_line.id)
				line._compute_amount()
			rec.paid_ids = ids

			rec.status1 = 'cashed'

		# Create Payment from info :
		# invoice_move_id = False
		#
		# for line in rec.invoice_ids.filtered(lambda inv: inv.check == True):
		#     invoice_move_id = line
		#
		# payment_vals = {
		#     'date': rec.cheque_date,
		#     'move_id': invoice_move_id,
		#     'amount': rec.amount,
		#     'payment_type': 'inbound',
		#     'partner_type': rec.partner_type,
		#     'journal_id': rec.journal_id.id,
		#     'currency_id': rec.company_id.currency_id.id,
		#     'partner_id': rec.payee_user_id.id,
		#     'partner_bank_id': rec.journal_id.bank_account_id.id,
		#     'destination_account_id': rec.debit_account_id.id,
		# }

	def action_outgoing_cashed(self):

		for rec in self:

			if rec.is_no_accounting_effect:
				rec.no_accounting_effect_state('cashed')
				continue
			# account_cheque = self.env['account.cheque'].browse(rec.id)
			account_move_obj = self.env['account.move']
			move_lines = []
			# if account_cheque.re_amount:

			vals = {
				'date': rec.cheque_given_date,
				'journal_id': rec.journal_id.id,
				'company_id': rec.company_id.id,
				'state': 'draft',
				'ref': rec.cheque_number + '- ' + 'Cashed',
				'account_cheque_id': rec.id
			}
			account_move = account_move_obj.create(vals)
			debit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': rec.credit_account_id.id,
				# 'debit' : account_cheque.re_amount,
				'debit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, debit_vals))
			credit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': rec.journal_id.default_account_id.id,
				# 'credit' : account_cheque.re_amount,
				'credit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, credit_vals))
			account_move.write({'line_ids': move_lines})
			
			account_move._post(soft=False)


			cheque_move = self.env['account.move'].search([('is_move_to_reconcile','=',True),('state','=','posted'),('account_cheque_id','=',rec.id)])
			dest_line = cheque_move.line_ids.filtered(lambda mv: mv.account_id.id == rec.debit_account_id.id)
			
			ids = []
			for line in rec.invoice_ids.filtered(lambda inv: inv.check == True):
				ids.append(line.id)
				line.js_assign_outstanding_line(dest_line.id)
				line._compute_amount()
			rec.paid_ids = ids
			
			rec.status = 'cashed'
		# return account_move

	@api.onchange('journal_id', 'cheque_book_id')
	def onchange_journal_id_change_cheque_book_id(self):
		for rec in self:
			if not rec.journal_id:
				rec.cheque_book_id = rec.cheque_book_line_id = False
			if not rec.cheque_book_id:
				rec.cheque_book_line_id = False

	@api.onchange('cheque_book_id', 'cheque_book_line_id')
	def onchange_set_cheque_number(self):
		for rec in self:
			rec.cheque_number = False
			if rec.cheque_book_line_id:
				rec.cheque_number = rec.cheque_book_line_id.name

	def no_accounting_effect_state(self, state='draft'):
		for rec in self:
			if rec.account_cheque_type == 'outgoing':
				rec.status = state
			else:
				rec.status1 = state

	def open_payment_matching_screen(self):
		# Open reconciliation view for customers/suppliers
		move_line_id = False
		account_move_line_ids = self.env['account.move.line'].search([('partner_id','=',self.payee_user_id.id)])
		for move_line in account_move_line_ids:
			if move_line.account_id.reconcile:
				move_line_id = move_line.id
				break;
		action_context = {'company_ids': [self.company_id.id], 'partner_ids': [self.payee_user_id.id]}
		if self.account_cheque_type == 'incoming':
			action_context.update({'mode': 'customers'})
		elif self.account_cheque_type == 'outgoing':
			action_context.update({'mode': 'suppliers'})
		if account_move_line_ids:
			action_context.update({'move_line_id': move_line_id})


		return {
			'type': 'ir.actions.client',
			'tag': 'manual_reconciliation_view',
			'context': action_context,
		}

	@api.depends('in_count', 'sequence', 'cheque_number')
	def _get_in_count(self):
		self.in_count = False
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				if self.sequence:
					ref = self.sequence + '- ' + self.cheque_number + '- ' + 'Registered'
				else:
					ref = self.cheque_number + '- ' + 'Registered'
				reference = ref
				if self.account_cheque_type == 'incoming':				
					credit_account = line.search([('ref','=',reference),('account_id','=',self.credit_account_id.id)])
					if credit_account:
						for record in credit_account:
							if record.reconciled == True:
								self.write({'status1':'cashed'})
				# if self.account_cheque_type == 'outgoing':
				# 	debit_account = line.search([('ref','=',reference),('account_id','=',self.debit_account_id.id)])
				# 	if debit_account:
				# 		for record in debit_account:
				# 			if record.reconciled == True:
				# 				self.write({'status':'cashed'})

		if self.amount != self.re_amount:
			self.write({'is_partial':True}) 
		else:
			self.write({'is_partial':False})

	@api.depends('status', 'status1', 'payee_user_id')
	def _get_outstanding_info(self):
		for record in self:
			if record.account_cheque_type == 'incoming':
				if record.status1 in ('return', 'deposited', 'transfered', 'cashed', 'bounced'):
					record.re_amount = 0.0
				else:
					record.re_amount = record.amount
			if record.account_cheque_type == 'outgoing': 
				if record.status in ('return','transfered','cashed','bounced'):
					record.re_amount = 0.0
				else:
					record.re_amount = record.amount
			for move in record.payee_user_id.invoice_ids:
				move.invoice_outstanding_credits_debits_widget = json.dumps(False)
				move.invoice_has_outstanding = False

				if move.state != 'posted' \
						or move.payment_state not in ('not_paid', 'partial') \
						or not move.is_invoice(include_receipts=True):
					continue

				pay_term_lines = move.line_ids\
					.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))

				domain = [
					('account_id', 'in', pay_term_lines.account_id.ids),
					('move_id.state', '=', 'posted'),('move_id.account_cheque_id','=',record.id),
					('partner_id', '=', move.commercial_partner_id.id),
					('reconciled', '=', False),
					'|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
				]

				payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

				if move.is_inbound():
					domain.append(('balance', '<', 0.0))
					payments_widget_vals['title'] = _('Outstanding credits')
				else:
					domain.append(('balance', '>', 0.0))
					payments_widget_vals['title'] = _('Outstanding debits')

				for lines in self.env['account.move.line'].search(domain):

					if record.account_cheque_type == 'incoming':
						if record.status1 not in ('return', 'deposited', 'transfered', 'cashed', 'bounced'):

							for line in lines:
								# get the outstanding residual value in invoice currency
								if line.currency_id and line.currency_id == move.currency_id:
									amount_to_show = abs(line.amount_residual_currency)
								else:
									currency = line.company_id.currency_id
									amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
																	   line.date or fields.Date.today())
									
								if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
									continue
								record.re_amount = amount_to_show
					if record.account_cheque_type == 'outgoing':
						if record.status not in ('return', 'transfered', 'cashed', 'bounced'):
							for line in lines:
								# get the outstanding residual value in invoice currency
								if line.currency_id and line.currency_id == move.currency_id:
									amount_to_show = abs(line.amount_residual_currency)
								else:
									currency = line.company_id.currency_id
									amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
																	   line.date or fields.Date.today())
									
								if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
									continue
								record.re_amount = amount_to_show



	@api.depends('name')
	def _active_journal_items(self):
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)
		item_count = len(list_of_move_line)
		journal_items.journal_items_count = item_count
		return
		
	def action_view_jornal_items(self):
		self.ensure_one()
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)
		return {
			'name': 'Journal Items',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'account.move.line',
			'domain': [('id', '=', list_of_move_line)],
		}

	@api.depends('attchment_ids')
	def _get_attachment_count(self):
		for cheque in self:
			attachment_ids = self.env['ir.attachment'].search([('account_cheque_id', '=', cheque.id)])
			cheque.attachment_count = len(attachment_ids)
		
	def attachment_on_account_cheque(self):
		self.ensure_one()
		return {
			'name': 'Attachment.Details',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'ir.attachment',
			'domain': [('account_cheque_id', '=', self.id)],
		}


	def set_from_deposite_to_draft(self):
		account_move = False
		
		
		#uncheck cheque book
		# if self.account_cheque_type == 'incoming':
		# 	if self.cheque_book_line_id:
		# 		self.cheque_book_line_id.is_used = False
		# 		self.cheque_book_line_id.account_cheque_id = False
		

		if self.is_no_accounting_effect:
			self.no_accounting_effect_state('registered')

		
		
			
			return
			
		account_move_obj = self.env['account.move']
		move_lines = []
		if self.account_cheque_type == 'incoming':
			vals = {
					'commercial_partner_id':self.payee_user_id.id,
					'date' : self.cheque_receive_date,
					'journal_id' : self.journal_id.id,
					'company_id' : self.company_id.id,
					'state' : 'draft',
					'ref' :self.cheque_number + '- ' + 'Registered Reverse' ,
					'account_cheque_id' : self.id,
					'is_move_to_reconcile':True
			}
			account_move = account_move_obj.create(vals)

			debit_vals = {
					'partner_id' : self.payee_user_id.id,
					'account_id' : self.credit_account_id.id,
					'debit' : self.amount,
					'date_maturity' : datetime.now().date(),
					'move_id' : account_move.id,
					'company_id' : self.company_id.id,
			}
			move_lines.append((0, 0, debit_vals))

			credit_vals = {
					'partner_id' : self.payee_user_id.id,
					'account_id' : self.debit_account_id.id,
					'credit' : self.amount,
					'date_maturity' : datetime.now().date(),
					'move_id' : account_move.id,
					'company_id' : self.company_id.id,
			}
			move_lines.append((0, 0, credit_vals))
			account_move.write({'line_ids' : move_lines})

			account_move._post(soft=False)
			self.status1 = 'draft'
		
	
	
		self.action_set_draft()


	def set_to_submit(self):
		print ("@@@@@@@@@@@@@@@@set_to_submitset_to_submit")
		account_move = False
		if not self.is_no_accounting_effect:
			if self.amount:
				account_move_obj = self.env['account.move']
				move_lines = []
				if self.account_cheque_type == 'incoming':
					vals = {
							'commercial_partner_id':self.payee_user_id.id,
							'date' : self.cheque_receive_date,
							'journal_id' : self.journal_id.id,
							'company_id' : self.company_id.id,
							'state' : 'draft',
							'ref' :self.cheque_number + '- ' + 'Registered' ,
							'account_cheque_id' : self.id,
							'is_move_to_reconcile':True
					}
					account_move = account_move_obj.create(vals)

					debit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.debit_account_id.id,
							'debit' : self.amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, debit_vals))

					credit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.credit_account_id.id,
							'credit' : self.amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, credit_vals))
					account_move.write({'line_ids' : move_lines})

					account_move._post(soft=False)
					self.status1 = 'registered'
				else:
					vals = {
							'commercial_partner_id':self.payee_user_id.id,
							'date' : self.cheque_given_date,
							'journal_id' : self.journal_id.id,
							'company_id' : self.company_id.id,
							'state' : 'draft',
							'ref' : self.cheque_number + '- ' + 'Registered',
							'account_cheque_id' : self.id,
							'is_move_to_reconcile':True
					}
					account_move = account_move_obj.create(vals)
					debit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.debit_account_id.id,
							'debit' : self.amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, debit_vals))
					credit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.credit_account_id.id,
							'credit' : self.amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, credit_vals))
					account_move.write({'line_ids' : move_lines})
					account_move._post(soft=False)
					self.status = 'registered'
				# return account_move
			else:
				raise UserError(_('Please Enter Amount Of Cheque'))
		else:
			
			self.no_accounting_effect_state('registered')

		for rec in self:
			
			if rec.cheque_book_line_id:
				rec.cheque_book_line_id.is_used = True
				rec.cheque_book_line_id.account_cheque_id = rec.id


	def set_to_bounced(self):
		if self.is_no_accounting_effect:
			self.no_accounting_effect_state('bounced')
			return
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
			journal_item_ids.button_cancel()

		account_move_obj = self.env['account.move']
		move_lines = []
		# if self.re_amount:
		if self.amount:
			if self.account_cheque_type == 'incoming':
				self.set_to_return()
				vals = {
					'date': self.cheque_receive_date,
					'journal_id': self.journal_id.id,
					'company_id': self.company_id.id,
					'state': 'draft',
					'ref': self.cheque_number + '- ' + 'Bounced',
					'account_cheque_id': self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.credit_account_id.id,
					# 'debit' : self.re_amount,
					'debit': self.amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
					'partner_id': self.payee_user_id.id,
					# 'account_id' : self.payee_user_id.property_account_receivable_id.id,
					'account_id': self.debit_account_id.id,
					# 'credit' : self.re_amount,
					'credit': self.amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids': move_lines})
				account_move._post(soft=False)

				# account_move.button_cancel()
				self.status1 = 'bounced'
			else:
				vals = {
					'date': self.cheque_given_date,
					'journal_id': self.journal_id.id,
					'company_id': self.company_id.id,
					'state': 'draft',
					'ref': self.cheque_number + '- ' + 'Bounced',
					'account_cheque_id': self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.credit_account_id.id,  # self.payee_user_id.property_account_payable_id.id,
					'debit': self.re_amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.debit_account_id.id,
					'credit': self.re_amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids': move_lines})
				account_move._post(soft=False)
				account_move.button_cancel()
				self.status = 'bounced'
			return account_move

	
	def action_incoming_return_to_deposited(self):
		if self.is_no_accounting_effect:
			self.no_accounting_effect_state('deposited')
			return
		for rec in self:
			cheque_last_move = self.env['account.move'].search([('state','=','posted'),('account_cheque_id','=',rec.id)],order="id desc",limit=1)
			
			# account_cheque = self.env['account.cheque'].browse(rec.id)
			account_move_obj = self.env['account.move']
			move_lines = []
			# if account_cheque.re_amount:
			if not self.env.user.company_id.deposite_account_id.id:
				raise UserError(("Sorry Please First Set Deposit account in Accounting Setting."))
			vals = {
				'date': rec.cheque_date,
				'journal_id': rec.journal_id.id,
				'company_id': rec.company_id.id,
				'state': 'draft',
				'ref': rec.cheque_number + '- ' + 'Cashed Reversed',
				'account_cheque_id': rec.id,
				
			}
			account_move = account_move_obj.create(vals)
			debit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': self.env.user.company_id.deposite_account_id.id,
				# 'debit' : account_cheque.re_amount,
				'debit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, debit_vals))
			credit_vals = {
				'partner_id': rec.payee_user_id.id,
				'account_id': rec.journal_id.default_account_id.id,
				# 'credit' : account_cheque.re_amount,
				'credit': rec.amount,
				'date_maturity': datetime.now().date(),
				'move_id': account_move.id,
				'company_id': rec.company_id.id,
			}
			move_lines.append((0, 0, credit_vals))
			account_move.write({'line_ids': move_lines})

			account_move._post(soft=False)
			account_move.button_cancel()
			cheque_last_move.button_cancel()

			
			
			rec.status1 = 'deposited'
	
	

	def set_to_return(self):
		if self.is_no_accounting_effect and self.account_cheque_type == 'incoming':
			# return
			self.no_accounting_effect_state('registered')
			return
		elif self.is_no_accounting_effect and self.account_cheque_type == 'outgoing':
			self.no_accounting_effect_state('return')
			return
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
			journal_item_ids.button_cancel()

		account_move_obj = self.env['account.move']
		move_lines = []
		list_of_move_line = []
		# if self.re_amount:
		if self.amount:

			for journal_items in self:
				journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])

			matching_dict = []
			for move in journal_item_ids:
				for line in move.line_ids:
					if line.full_reconcile_id:
						matching_dict.append(line)

			if len(matching_dict) != 0:
				rec_id = matching_dict[0].full_reconcile_id.id
				a = self.env['account.move.line'].search([('full_reconcile_id', '=', rec_id)])

				for move_line in a:
					move_line.remove_move_reconcile()

			if self.account_cheque_type == 'incoming':
				if not self.env.user.company_id.deposite_account_id.id:
					raise UserError(("Sorry Please First Set Deposit account in Accounting Setting."))
				vals = {
					'date': self.cheque_receive_date,
					'journal_id': self.journal_id.id,
					'company_id': self.company_id.id,
					'state': 'draft',
					'ref': self.cheque_number + '- ' + 'Returned',
					'account_cheque_id': self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.debit_account_id.id,
					# 'debit' : self.re_amount,
					'debit': self.amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.env.user.company_id.deposite_account_id.id,
					# 'credit' : self.re_amount,
					'credit': self.amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids': move_lines})
				account_move._post(soft=False)
				# account_move.button_cancel()
				# self.status1 = 'return'
				# as docs states
				self.status1 = 'registered'
				self.cheque_return_date = datetime.now().date()
			else:
				vals = {
					'date': self.cheque_given_date,
					'journal_id': self.journal_id.id,
					'company_id': self.company_id.id,
					'state': 'draft',
					'ref': self.cheque_number + '- ' + 'Returned',
					'account_cheque_id': self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.credit_account_id.id,
					'debit': self.re_amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
					'partner_id': self.payee_user_id.id,
					'account_id': self.debit_account_id.id,
					'credit': self.re_amount,
					'date_maturity': datetime.now().date(),
					'move_id': account_move.id,
					'company_id': self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids': move_lines})
				account_move._post(soft=False)
				account_move.button_cancel()
				self.status = 'return'
				self.cheque_return_date = datetime.now().date()
			return account_move

	def set_to_deposite(self):
		if self.is_no_accounting_effect:
			self.no_accounting_effect_state('deposited')
			return

		account_move_obj = self.env['account.move']
		move_lines = []
		if self.amount:
			if self.account_cheque_type == 'incoming':
				vals = {
						'date' : self.cheque_receive_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Deposited',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				# res = self.env['res.config.settings'].search([], limit=1, order="id desc")
				# if res:
				print ("\n\n\n self.env.user.company_id", self.env.user.company_id.name)
				print ("\n\n\n self.env.user.company_id", self.company_id.deposite_account_id.code)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.company_id.deposite_account_id.id,
						# 'debit' : self.re_amount,
						'debit': self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id,
						# 'credit' : self.re_amount,
						'credit': self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				# else:
				# 	debit_vals = {
				# 			'partner_id' : self.payee_user_id.id,
				# 			'account_id' : self.credit_account_id.id,
				# 			'debit' : self.re_amount,
				# 			'date_maturity' : datetime.now().date(),
				# 			'move_id' : account_move.id,
				# 			'company_id' : self.company_id.id,
				# 	}
				# 	move_lines.append((0, 0, debit_vals))
				# 	credit_vals = {
				# 			'partner_id' : self.payee_user_id.id,
				# 			'account_id' : self.debit_account_id.id,
				# 			'credit' : self.re_amount,
				# 			'date_maturity' : datetime.now().date(),
				# 			'move_id' : account_move.id,
				# 			'company_id' : self.company_id.id,
				# 	}
				# 	move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids': move_lines})
				
				account_move._post(soft=False)
				
				self.status1 = 'deposited'
				
				return account_move          
				
	def set_to_cancel(self):
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id', '=', journal_items.id)])
			journal_item_ids.button_cancel()
			journal_item_ids.button_draft()
			journal_item_ids.button_cancel()
		self.paid_ids = False
		if self.account_cheque_type == 'incoming':
			self.status1 = 'cancel'
		else:
			self.status = 'cancel'
		
		self.re_compute_invoice()	

	def action_set_draft(self):
		for rec in self:
			rec.set_to_cancel()
			rec.status = rec.status1 = 'draft'
			rec.re_compute_invoice()	

		if rec.cheque_book_line_id:
			rec.cheque_book_line_id.is_used = False
			rec.cheque_book_line_id.account_cheque_id = False

	"""
		using for cheque amount O2M line if value come + checkbox true  
	"""
	@api.onchange('invoice_ids', 'cheque_operation_ids')
	def onchange_set_cheque_amount(self):
		for rec in self:
			amount = 0
			for line in self.invoice_ids:
				if line.check:
					id = line.id or line.id.origin
					if rec.payee_user_id:
						account_move = self.env['account.move']
						move_line = account_move.search([('id', '=', id)], limit=1)
						line.curr_due_amount = move_line.amount_residual
					amount += line.curr_due_amount
					rec.currency_id = line.currency_id.id
			for line in rec.cheque_operation_ids:
				if line.check:
					amount += line.amount

	@api.onchange('payee_user_id')
	def onchange_payee_user_id_set_op(self):
		for rec in self:
			if rec.payee_user_id:
				acp_object = self.env['account.cheque.operation']
				acps = acp_object.search([('partner_id', '=', rec.payee_user_id.id), ('check', '=', False), ])

				acps_records = []
				# when fix dopmain use orm search only
				for acp in acps:
					if acp.account_payment_id.state != 'posted' and acp.account_cheque_id.status != 'cashed':
						acps_records.append(acp.id)
				rec.cheque_operation_ids = acps_records  # acps.ids


			else:
				rec.cheque_operation_ids = False

	@api.onchange('journal_id')
	def onchange_journal_set_account(self):
		for rec in self:
			if rec.journal_id:
				if rec.journal_id.default_account_id:
					rec.bank_account_id = rec.journal_id.default_account_id.id
				else:
					rec.bank_account_id = False
				# raise UserError(('Please Config Bank account in Jounral Configuration First'))
			else:
				rec.bank_account_id = False


class ChequeWizard(models.TransientModel):
	_name = 'cheque.wizard'
	_description = "cheque.wizard"

	@api.model 
	def default_get(self, flds): 
		result = super(ChequeWizard, self).default_get(flds)
		account_cheque_id = self.env['account.cheque'].browse(self._context.get('active_id'))
		if account_cheque_id.account_cheque_type == 'outgoing':
			result['is_outgoing'] = True
		return result
		
	def create_cheque_entry(self):
		account_cheque = self.env['account.cheque'].browse(self._context.get('active_ids'))
		account_move_obj = self.env['account.move']
		move_lines = []
		if account_cheque.re_amount:
			if account_cheque.account_cheque_type == 'incoming':
				vals = {
						'date' : self.chequed_date,
						'journal_id' : self.cash_journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Cashed',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.debit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.bank_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				account_cheque.status1 = 'cashed'
			else:
				vals = {
						'date' : self.chequed_date,
						'journal_id' : self.cash_journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Cashed',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.credit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : self.bank_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				account_cheque.status = 'cashed'
			return account_move

	cash_journal_id = fields.Many2one('account.journal',string="Cash Journal",required=True,domain=[('type', '=', 'cash')])
	chequed_date = fields.Date(string="Cheque Date")
	bank_account_id = fields.Many2one('account.account',string="Bank Account")
	is_outgoing = fields.Boolean(string="Is Outgoing",default=False)
	
class ChequeTransferedWizard(models.TransientModel):
	_name = 'cheque.transfered.wizard'
	_description = "cheque.transfered.wizard"

	def create_ckeck_transfer_entry(self):
		account_cheque = self.env['account.cheque'].browse(self._context.get('active_ids'))
		account_move_obj = self.env['account.move']
		move_lines = []
		for journal_items in account_cheque:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			journal_item_ids.button_cancel()

		if account_cheque.re_amount:
			if account_cheque.account_cheque_type == 'incoming':
				vals = {
						'date' : self.transfered_date,
						'journal_id' : account_cheque.journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Transfered',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.contact_id.id,
						'account_id' : account_cheque.credit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.contact_id.id,
						'account_id' : account_cheque.debit_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_cheque.status1 = 'transfered'
				account_cheque.payee_user_id = self.contact_id.id
				return account_move
		
	transfered_date = fields.Date(string="Transfered Date")
	contact_id = fields.Many2one('res.partner',string="Contact")
	

class ReportWizard(models.TransientModel):
	_name = "report.wizard"
	_description = "report.wizard"

	from_date = fields.Date('From Date', required = True)
	to_date = fields.Date('To Date',required = True)
	cheque_type = fields.Selection([('incoming','Incoming'),('outgoing','Outgoing')],string="Cheque Type",default='incoming')
	
	
	def submit(self):
		inc_temp = []
		out_temp = []
		temp = [] 
		
		if self.cheque_type == 'incoming':
			in_account_cheque_ids = self.env['account.cheque'].search([(str('cheque_date'),'>=',self.from_date),(str('cheque_date'),'<=',self.to_date),('account_cheque_type','=','incoming')])
		
			if not in_account_cheque_ids:
				raise UserError(_('There Is No Any Cheque Details.'))
			else:
				for inc in in_account_cheque_ids:
					temp.append(inc.id)
			
		if self.cheque_type == 'outgoing':
			out_account_cheque_ids = self.env['account.cheque'].search([(str('cheque_date'),'>=',self.from_date),(str('cheque_date'),'<=',self.to_date),('account_cheque_type','=','outgoing')])
			
			if not out_account_cheque_ids:
				raise UserError(_('There Is No Any Cheque Details.'))
			else:
				for out in out_account_cheque_ids:
					temp.append(out.id)
							   
		data = temp
		in_data = inc_temp
		out_data = out_temp
		datas = {
			'ids': self._ids,
			'model': 'account.cheque',
			'form': data,
			'from_date':self.from_date,
			'to_date':self.to_date,
			'cheque_type' : self.cheque_type,
		}
		return self.env.ref('bi_account_cheque.account_cheque_report_id').report_action(self,data=datas)

class IrAttachment(models.Model):
	_inherit='ir.attachment'

	account_cheque_id  =  fields.Many2one('account.cheque', 'Attchments')


class accountChequeOperation(models.Model):
	_name = "account.cheque.operation"

	name = fields.Char()
	amount = fields.Float()
	partner_id = fields.Many2one('res.partner')
	payslip_id = fields.Many2one('hr.payslip')
	loan_id = fields.Many2one('hr.loan')
	salary_advance_id = fields.Many2one('salary.advance')
	account_cheque_id = fields.Many2one('account.cheque')
	account_payment_id = fields.Many2one('account.payment')
	check = fields.Boolean()


