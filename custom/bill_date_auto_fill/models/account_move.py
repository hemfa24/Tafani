from odoo import models, fields, api
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date = fields.Date(string='Invoice/Bill Date', default=fields.Date.context_today, required=True)

    @api.model
    def create(self, vals):
        if not vals.get('invoice_date'):
            vals['invoice_date'] = fields.Date.context_today(self)
        return super(AccountMove, self).create(vals)

    def write(self, vals):
        if 'invoice_date' in vals and not vals['invoice_date']:
            vals['invoice_date'] = fields.Date.context_today(self)
        return super(AccountMove, self).write(vals)
