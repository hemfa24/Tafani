# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.osv import expression

class AccountFiscalyear(models.Model):
	_inherit = "account.fiscalyear"
	_description = "Fiscal Year"
	_order = 'date_start, id'

	name = fields.Char('Fiscal Year')
	code = fields.Char('Code', size=6)
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
	date_start = fields.Date('Start Date')
	date_stop = fields.Date('End Date')
	period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
	state = fields.Selection(selection_add=[
							('draft','Open'),
							('waiting_approval','Waiting for Approval'),
							('done','Closed'),
							('waiting_reopen_approval','Waiting for Re-Open Approval')],
							ondelete={
							'draft': 'cascade',
							'waiting_approval': 'cascade',
							'done': 'cascade',
							'waiting_reopen_approval': 'cascade'})
	end_journal_period_id = fields.Many2one('account.journal.period', 'End of Year Entries Journal', readonly=True, copy=False)

	def action_waiting_approval(self):
		mode = 'done'
		for record in self:
			self._cr.execute('UPDATE account_journal_period SET state = %s WHERE period_id IN ( SELECT id FROM account_period WHERE fiscalyear_id = %s)',('done', record.id))
			self._cr.execute('UPDATE account_period SET state = %s WHERE fiscalyear_id = %s', (mode, record.id))
			self._cr.execute('UPDATE account_fiscalyear SET state = %s WHERE id = %s', (mode, record.id))
		return True


	def action_waiting_reopen_approval(self):
		mode = 'draft'
		for record in self:
			if self.user_has_groups('advance_fiscal_year_sync_approval_app.group_period_approval_reopen'):
				self._cr.execute('UPDATE account_journal_period SET state = %s WHERE period_id IN ( SELECT id FROM account_period WHERE fiscalyear_id = %s)',('done', record.id))
				self._cr.execute('UPDATE account_period SET state = %s WHERE fiscalyear_id = %s', (mode, record.id))
			self._cr.execute('UPDATE account_fiscalyear SET state = %s WHERE id = %s', (mode, record.id))
		return True


class AccountPeriod(models.Model):
	_inherit = "account.period"
	_description = "Account period"

	name = fields.Char('Period Name')
	code = fields.Char('Code', size=12)
	special = fields.Boolean('Opening/Closing Period',help="These periods can overlap.")
	date_start = fields.Date('Start of Period')
	date_stop = fields.Date('End of Period')
	fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year')
	state = fields.Selection(selection_add=[
							('draft','Open'),
							('waiting_approval','Waiting for Approval'),
							('done','Closed'),
							('waiting_reopen_approval','Waiting for Re-Open Approval')],
							ondelete={
							'draft': 'cascade',
							'waiting_approval': 'cascade',
							'done': 'cascade',
							'waiting_reopen_approval': 'cascade'})
	company_id = fields.Many2one('res.company', string='Company', store=True, readonly=True, default=lambda self: self.env.user.company_id )

	_sql_constraints = [
		('name_only_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
	]

	@api.returns('self')
	def find(self, dt=None):
		context = (self._context or {})
		if not dt:
			dt = fields.Date.context_today(self)
		args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
		if context.get('company_id', False):
			args.append(('company_id', '=', context['company_id']))
		else:
			company_id = self.env.user.company_id.id
			args.append(('company_id', '=', company_id))
		result = []
		if context.get('account_period_prefer_normal', True):
			# look for non-special periods first, and fallback to all if no result is found
			result = self.search(args + [('special', '=', False)])
		if not result:
			result = self.search(args)
		if not result:
			action = self.env.ref('advance_fiscal_year_sync_approval_app.action_account_period')
			msg = _('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.')
			raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
		return result


	def action_waiting_approval(self):
		mode = 'done'
		for record in self:
			self._cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(record.ids),))
			self._cr.execute('update account_period set state=%s where id in %s', (mode, tuple(record.ids),))
		return True


	def action_waiting_reopen_approval(self):
		mode = 'draft'
		for record in self:
			self._cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(record.ids),))
			self._cr.execute('update account_period set state=%s where id in %s', (mode, tuple(record.ids),))
		return True


