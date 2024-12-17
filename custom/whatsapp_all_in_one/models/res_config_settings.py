# -*- coding: utf-8 -*-

import os
import shutil

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_whatsapp_invoice = fields.Boolean(string='Automatic Receipt/Invoice via WhatsApp', help="Send POS Receipt/Invoice Automatically to Customer's WhatsApp Number")
    default_option = fields.Selection([('invoice', 'Invoice'), ('receipt', 'Receipt')], string='WhatsApp Default Option', default='receipt', default_model='pos.config')

    @api.onchange('default_option', 'module_account')
    def _onchange_default_option(self):
        if self.default_option == 'invoice' and not self.module_account:
            raise UserError(_("You can't set invoice as default option, becuase invoicing option is not enabled."))

    def action_logout(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.abspath(dir_path + '/../wizard')
        data_dir = '.user_data_uid_' + self._get_unique_user()
        try:
            self.env['whatsapp.msg'].sudo()._cron_kill_chromedriver()
            shutil.rmtree(dir_path + '/' + data_dir)
        except:
            pass

    def _get_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)
