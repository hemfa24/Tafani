# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountReOpenFiscalYearClose(models.TransientModel):
	_name = "account.reopen.fiscalyear.close"
	_description = "Account Reopen Fiscal Year Close"

	sure = fields.Boolean('Check this box')

	def data_save(self):
		active_ids = self._context.get('active_ids')
		fiscalyear_ids = self.env['account.fiscalyear'].browse(active_ids)
		for record in self:
			if record.sure:
				mode = 'waiting_reopen_approval'
				for fiscal in fiscalyear_ids:
					self._cr.execute('update account_fiscalyear set state=%s where id in %s', (mode, tuple(fiscal.ids),))
					self._cr.execute('update account_period set state=%s where fiscalyear_id in %s', (mode, tuple(fiscal.ids),))
		return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
