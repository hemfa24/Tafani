# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountReOpenPeriodClose(models.TransientModel):
    _name = "account.reopen.period.close"
    _description = "Account Reopen Period Close"

    sure = fields.Boolean('Check this box')


    def data_save(self):
        account_move_obj = self.env['account.move']
        active_ids = self._context.get('active_ids')
        period_ids = self.env['account.period'].browse(active_ids)
        for record in self:
            if record.sure:
                mode = 'waiting_reopen_approval'
                for period_id in period_ids:
                    if period_id.fiscalyear_id.state in ('done', 'waiting_reopen_approval'):
                        raise UserError(_('You can not re-open a period which belongs to closed fiscal year'))
                    self._cr.execute('update account_period set state=%s where id in %s', (mode, tuple(period_id.ids),))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
