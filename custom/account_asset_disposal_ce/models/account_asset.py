# -*- coding: utf-8 -*-
#from openerp import models, fields, api, _
#from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category.custom'

    disposal_account_id = fields.Many2one(
        'account.account',
        string='Disposal Account(Writeoff)',
    )
    disposal_journal_id = fields.Many2one(
        'account.journal',
        string='Disposal Journal(Writeoff)',
    )
    disposal_sale_account_id = fields.Many2one(
        'account.account',
        string='Disposal Account(Sale)',
    )
    disposal_sale_journal_id = fields.Many2one(
        'account.journal',
        string='Disposal Journal(Sale)',
    )


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset.custom'

    use_disposal = fields.Boolean(
        string="Use Asset Disposal?",
    )
    diposal_type = fields.Selection(
        [('sale', 'Sale'),
         ('write_off', 'Write-Off')],
        string='Disposal Type',
    )
    writeoff_move_id =  fields.Many2one(
        'account.move',
        string='Write-Off Entry',
        readonly=True,
        copy=False,
    )
    disposal_date = fields.Date(
        string='Disposal Date',
        default=fields.Date.today(),
    )
    writeoff_account_id = fields.Many2one(
        'account.account',
        string='Write-Off Account',
        copy=False,
    )
    sale_account_id = fields.Many2one(
        'account.account',
        string='Disposal Account',
        copy=False,
    )
    writeoff_journal_id = fields.Many2one(
        'account.journal',
        string='Write-Off Journal',
        copy=False,
    )
    sale_journal_id = fields.Many2one(
        'account.journal',
        string='Disposal Journal',
        copy=False,
    )
    disposal_invoice_id = fields.Many2one(
#        'account.invoice',
        'account.move',
        string='Customer Invoice',
        copy=False,
    )
    depriciation_move_id = fields.Many2one(
        'account.move',
        string='Depreciation Entry',
        readonly=True,
        copy=False,
    )
    depriciation_move_created = fields.Boolean(
        string='Depreciation Entry Created',
        copy=False
    )
    writeoff_move_created = fields.Boolean(
        string='Writeoff Entry Created',
        copy=False
    )
    asset_move_id = fields.Many2one(
        'account.move',
        string='Asset Entry',
        readonly=True,
        copy=False,
    )
    disposal_partner_id = fields.Many2one(
        'res.partner',
        string='Disposal Customer',
#        domain="[('customer', '=', True)]",
    )
    invoice_amount = fields.Monetary(
        related='disposal_invoice_id.amount_total',
        string='Invoice Amount',
    )

    @api.onchange('category_id')
    def onchange_category_id(self):
        res = super(AccountAssetAsset, self).onchange_category_id()
        if self.category_id:
            # writeoff
            self.writeoff_account_id = self.category_id.disposal_account_id or False
            self.writeoff_journal_id = self.category_id.disposal_journal_id or False
            #sale
            self.sale_account_id = self.category_id.disposal_sale_account_id or False
            self.sale_journal_id = self.category_id.disposal_sale_journal_id or False
        return res

    @api.onchange('diposal_type')
    def onchange_diposal_type(self):
        if self.diposal_type and self.category_id:
            # writeoff
            self.writeoff_account_id = self.category_id.disposal_account_id or False
            self.writeoff_journal_id = self.category_id.disposal_journal_id or False
            #sale
            self.sale_account_id = self.category_id.disposal_sale_account_id or False
            self.sale_journal_id = self.category_id.disposal_sale_journal_id or False
        else:
            # writeoff
            self.writeoff_account_id = False
            self.writeoff_journal_id = False
            #sale
            self.sale_account_id = False
            self.sale_journal_id = False

    #@api.multi
    def create_accounting_entries(self):
        move_line_obj = self.env['account.move.line']
         
        if self.depreciation_line_ids:
            for line in self.depreciation_line_ids:
                if line.move_check:
                    if not line.move_id.state == 'posted':
                        raise UserError(_('Please post the move of all depreciation lines.'))
         
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        journal = self.writeoff_journal_id
        account = self.writeoff_account_id
         
        asset_name = 'Write-Off' + ' - ' + self.name
        reference  = self.name
        
        move_lines = []
        move_vals = {
        # 'name': asset_name,
        'date': self.disposal_date,
        'ref': reference,
        'journal_id': journal.id,
#        'type': 'entry',
        'move_type': 'entry',
        }
        move_id = self.env['account.move'].create(move_vals)#create the move
        
        purchase_amount = current_currency.compute(self.value, company_currency)
        if self.writeoff_journal_id.type == 'purchase':
            sign = 1
        else:
            sign = -1
        asset_name = 'Write offs ' + self.name
         
        value_residual = current_currency.compute(self.value_residual, company_currency)
        amount_purchase = self.value
        amount_residual = self.value_residual
        amount_residual_cur = current_currency.compute(amount_residual, company_currency)
        write_off_amount = amount_purchase - amount_residual
        write_off_amount_cur = current_currency.compute(write_off_amount, company_currency)
        moveline_vals = {
            'name': asset_name,
            'ref': reference,
            'move_id': move_id.id,
            'journal_id': journal.id,
            'partner_id': False,
#            'currency_id': company_currency.id != current_currency.id and current_currency.id or False,
            'currency_id': current_currency.id,
#            'analytic_account_id': self.category_id.account_analytic_id.id,
            'date': self.disposal_date,
#            'asset_id': self.id
            'custom_asset_id': self.id
        }
        if self.category_id.account_analytic_id:
            moveline_vals.update({
                'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
            })
        writeoff_moveline_vals= {
            # 'account_id': self.writeoff_account_id.id,
            'account_id': self.category_id.account_depreciation_id.id,  #FIX-22/04/2019
            'credit': 0.0,
            'debit': write_off_amount_cur,
            'amount_currency': company_currency.id != current_currency.id and sign * write_off_amount or 0.0,
            'currency_id': current_currency.id,
        }
        writeoff_moveline_vals.update(moveline_vals)
        move_lines.append((0, 0, writeoff_moveline_vals))
#         move_line_obj.create(writeoff_moveline_vals)
         
        depreciation_moveline_vals = {
            # 'account_id': self.category_id.account_depreciation_id.id,
            'account_id': self.writeoff_account_id.id,  #FIX-22/04/2019
            'debit': amount_residual_cur,
            'credit': 0.0,
            'amount_currency': company_currency.id != current_currency.id and -sign * value_residual or 0.0,
            'currency_id': current_currency.id,
        }
        depreciation_moveline_vals.update(moveline_vals)
        move_lines.append((0, 0, depreciation_moveline_vals))
#         move_line_obj.create(depreciation_moveline_vals)
         
        asset_moveline_vals = {
            'account_id': self.category_id.account_asset_id.id,
            'credit': purchase_amount,
            'debit': 0.0,
            'amount_currency': company_currency.id != current_currency.id and sign * amount_purchase or 0.0,
#            'analytic_account_id': self.category_id.account_analytic_id.id,
            'currency_id': current_currency.id,
        }
        if self.category_id.account_analytic_id:
            asset_moveline_vals.update({
                'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
            })
        asset_moveline_vals.update(moveline_vals)
        move_lines.append((0, 0, asset_moveline_vals))
#         move_line_obj.create(asset_moveline_vals)
        move_id.write({'line_ids': move_lines})
        self.write({'writeoff_move_id': move_id.id,
                    'writeoff_move_created': True})

#     #@api.multi #FIX-22/04/2019
#     def create_accounting_entries(self):
#         move_line_obj = self.env['account.move.line']
         
#         if self.depreciation_line_ids:
#             for line in self.depreciation_line_ids:
#                 if line.move_check:
#                     if not line.move_id.state == 'posted':
#                         raise UserError(_('Please post the move of all depreciation lines.'))
         
#         company_currency = self.company_id.currency_id
#         current_currency = self.currency_id
#         journal = self.writeoff_journal_id
#         account = self.writeoff_account_id
         
#         asset_name = 'Write-Off' + ' - ' + self.name
#         reference  = self.name
        
#         move_lines = []
#         print ("journal:-------------------",journal)
#         move_vals = {
#         'name': asset_name,
#         'date': self.disposal_date,
#         'ref': reference,
#         'journal_id': journal.id
#         }
#         move_id = self.env['account.move'].create(move_vals)#create the move
#         print ("move_id:-------------------------",move_id)
        
#         purchase_amount = current_currency.compute(self.value, company_currency)
#         print ("purchase_amount:--------------------",purchase_amount)
#         if self.writeoff_journal_id.type == 'purchase':
#             sign = 1
#         else:
#             sign = -1
#         asset_name = 'Write offs ' + self.name
         
#         value_residual = current_currency.compute(self.value_residual, company_currency)
#         amount_purchase = self.value
#         amount_residual = self.value_residual
#         amount_residual_cur = current_currency.compute(amount_residual, company_currency)
#         write_off_amount = amount_purchase - amount_residual
#         write_off_amount_cur = current_currency.compute(write_off_amount, company_currency)
         
#         moveline_vals = {
#             'name': asset_name,
#             'ref': reference,
#             'move_id': move_id.id,
#             'journal_id': journal.id,
#             'partner_id': False,
#             'currency_id': company_currency.id != current_currency.id and current_currency.id or False,
#             'analytic_account_id': self.category_id.account_analytic_id.id,
#             'date': self.disposal_date,
#             'asset_id': self.id
#         }
         
#         writeoff_moveline_vals= {
#             'account_id': self.writeoff_account_id.id,
#             'credit': 0.0,
#             'debit': write_off_amount_cur,
#             'amount_currency': company_currency.id != current_currency.id and sign * write_off_amount or 0.0,
#         }
#         writeoff_moveline_vals.update(moveline_vals)
#         move_lines.append((0, 0, writeoff_moveline_vals))
# #         move_line_obj.create(writeoff_moveline_vals)
         
#         depreciation_moveline_vals = {
#             'account_id': self.category_id.account_depreciation_id.id,
#             'debit': amount_residual_cur,
#             'credit': 0.0,
#             'amount_currency': company_currency.id != current_currency.id and -sign * value_residual or 0.0,
#         }
#         depreciation_moveline_vals.update(moveline_vals)
#         move_lines.append((0, 0, depreciation_moveline_vals))
# #         move_line_obj.create(depreciation_moveline_vals)
         
#         asset_moveline_vals = {
#             'account_id': self.category_id.account_asset_id.id,
#             'credit': purchase_amount,
#             'debit': 0.0,
#             'amount_currency': company_currency.id != current_currency.id and sign * amount_purchase or 0.0,
#             'analytic_account_id': self.category_id.account_analytic_id.id,
#         }
#         asset_moveline_vals.update(moveline_vals)
#         move_lines.append((0, 0, asset_moveline_vals))
# #         move_line_obj.create(asset_moveline_vals)

#         print ("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#         move_id.write({'line_ids': move_lines})
#         self.write({'writeoff_move_id': move_id.id,
#                     'writeoff_move_created': True})

# 
    #@api.multi
    def disposal_gain_loss(self):
        # purchase_value become value
        if not self.disposal_partner_id:
            raise UserError(_('Please select disposal customer!'))
        if not self.disposal_invoice_id:
            raise UserError(_('Please select customer invoice!'))
         
        invoice_amt = self.disposal_invoice_id.amount_total
        accumulated_value = self.value - self.value_residual
        move_line_obj = self.env['account.move.line']
        move_obj = self.env['account.move']
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        ctx = dict(self._context or {})
        ctx.update({'date': self.disposal_date})
        purchase_amount = current_currency.compute(self.value, company_currency)
        accumulated_amt = current_currency.compute(accumulated_value, company_currency)
        if self.sale_journal_id.type == 'purchase':
            sign = 1
        else:
            sign = -1
        asset_name = self.name
        reference = self.name
         
        journal_id = self.sale_journal_id.id
        partner_id = self.disposal_partner_id.id
         
        moveline_vals = {
            'name': 'Disposal - ' + asset_name,
            'ref': reference,
            'move_id': False,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'currency_id': company_currency.id != current_currency.id and  current_currency.id or False,
            'date': self.disposal_date,
        }
        if self.value_residual > invoice_amt:#loss
            move_vals = {
                'date': self.disposal_date,
                'ref': reference,
                'journal_id': self.sale_journal_id.id,
#                'type': 'entry',
                'move_type': 'entry',
            }
            move_id = move_obj.create(move_vals)
            move_lines = []
            moveline_vals.update({'move_id': move_id.id})
            asset_moveline_vals = {
                'account_id': self.category_id.account_asset_id.id,
                'credit': purchase_amount,
                'debit': 0.0,
                'amount_currency': company_currency.id != current_currency.id and -sign * self.value or 0.0,
            }
            asset_moveline_vals.update(moveline_vals)
            move_lines.append((0 ,0, asset_moveline_vals))
#             move_line_obj.create(asset_moveline_vals)
            disposal_moveline_vals = {
                'account_id': self.sale_account_id.id,
                'debit': purchase_amount,
                'credit': 0.0,
                'amount_currency': company_currency.id != current_currency.id and sign * self.value or 0.0,
#                'analytic_account_id': self.category_id.account_analytic_id.id,
#                'asset_id': self.id
                'custom_asset_id': self.id
            }
            if self.category_id.account_analytic_id:
                disposal_moveline_vals.update({
                    'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
                })
            disposal_moveline_vals.update(moveline_vals)
            move_lines.append((0 ,0, disposal_moveline_vals))
#             move_line_obj.create(disposal_moveline_vals)

            move_id.write({'line_ids': move_lines})
            self.write({'asset_move_id': move_id.id})
            move_vals = {
                'date': self.disposal_date,
                'ref': reference,
                'journal_id': self.sale_journal_id.id,
#                'type': 'entry',
                'move_type': 'entry',
            }
            move_id1 = move_obj.create(move_vals)
            disp_move_lines = []
            moveline_vals.update({'move_id': move_id1.id})
             
            disposal_moveline_vals2 = {
                'account_id': self.sale_account_id.id,
                'credit': accumulated_amt,
                'debit': 0.0,
                'amount_currency': company_currency.id != current_currency.id and -sign * accumulated_value or 0.0,
            }
            disposal_moveline_vals2.update(moveline_vals)
            disp_move_lines.append((0, 0, disposal_moveline_vals2))
#             move_line_obj.create(disposal_moveline_vals2)
             
            depr_moveline_vals = {
                'account_id': self.category_id.account_depreciation_id.id,
                'credit': 0.0,
                'debit': accumulated_amt,
                'amount_currency': company_currency.id != current_currency.id and sign * accumulated_value or 0.0,
#                'analytic_account_id': self.category_id.account_analytic_id.id,
#                'asset_id': self.id
                'custom_asset_id': self.id
            }
            if self.category_id.account_analytic_id:
                depr_moveline_vals.update({
                    'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
                })
            depr_moveline_vals.update(moveline_vals)
            disp_move_lines.append((0, 0, depr_moveline_vals))
            move_id1.write({'line_ids': disp_move_lines})
#             move_line_obj.create(depr_moveline_vals)
            self.write({'depriciation_move_id': move_id1.id})
        elif self.value_residual <= invoice_amt:#gain-profit
            move_vals = {
                'date': self.disposal_date,
                'ref': reference,
                'journal_id': self.sale_journal_id.id,
#                'type': 'entry',
                'move_type': 'entry',
            }
            move_id = move_obj.create(move_vals)
            move_lines = []
            moveline_vals.update({'move_id': move_id.id})
             
            asset_moveline_vals = {
                'account_id': self.category_id.account_asset_id.id,
                'debit': 0.0,
                'credit': self.value,
                'currency_id': company_currency.id != current_currency.id and  current_currency.id or False,
                'amount_currency': company_currency.id != current_currency.id and -sign * self.value or 0.0,
            }
            asset_moveline_vals.update(moveline_vals)
            move_lines.append((0, 0, asset_moveline_vals))
#             move_line_obj.create(asset_moveline_vals)
             
            disposal_moveline_vals = {
                'account_id': self.sale_account_id.id,
                'credit': 0.0,
                'debit': self.value,
                'amount_currency': company_currency.id != current_currency.id and sign * self.value or 0.0,
#                'analytic_account_id': self.category_id.account_analytic_id.id,
#                'asset_id': self.id
                'custom_asset_id': self.id
            }
            if self.category_id.account_analytic_id:
                disposal_moveline_vals.update({
                    'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
                })
            disposal_moveline_vals.update(moveline_vals)
            move_lines.append((0, 0, disposal_moveline_vals))
#             move_line_obj.create(disposal_moveline_vals)
            move_id.write({'line_ids': move_lines})
            self.write({'asset_move_id': move_id.id})
             
            move_vals = {
                'date': self.disposal_date,
                'ref': reference,
                'journal_id': self.sale_journal_id.id,
#                'type': 'entry',
                'move_type': 'entry',
            }
            move_id1 = move_obj.create(move_vals)
            disp_move_lines = []
            moveline_vals.update({'move_id': move_id1.id})
            disposal_moveline_vals1 = {
                'account_id': self.sale_account_id.id,
                'debit':0.0,
                'credit': accumulated_value,
                'amount_currency': company_currency.id != current_currency.id and -sign * accumulated_value or 0.0,
            }
            disposal_moveline_vals1.update(moveline_vals)
            disp_move_lines.append((0, 0, disposal_moveline_vals1))
#             move_line_obj.create(disposal_moveline_vals1)
             
            depr_moveline_vals = {
                'account_id': self.category_id.account_depreciation_id.id,
                'credit': 0.0,
                'debit':accumulated_value ,
                'amount_currency': company_currency.id != current_currency.id and sign * accumulated_value or 0.0,
#                'analytic_account_id': self.category_id.account_analytic_id.id,
#                'asset_id': self.id
                'custom_asset_id': self.id
            }
            if self.category_id.account_analytic_id:
                depr_moveline_vals.update({
                    'analytic_distribution': {self.category_id.account_analytic_id.id : 100},
                })
            depr_moveline_vals.update(moveline_vals)
            disp_move_lines.append((0, 0, depr_moveline_vals))
            move_id1.write({'line_ids': disp_move_lines})
#             move_line_obj.create(depr_moveline_vals)
            self.write({'depriciation_move_id': move_id1.id, 'depriciation_move_created': True})
        return True

    #@api.multi
    def action_asset_force_close(self):
        for asset in self:
            if asset.writeoff_move_created or asset.depriciation_move_created:
                asset.message_post(body=_("Document closed."))
                asset.write({'state': 'close'})
            else:
                raise UserError(_(
                    'You can not close asset because this asset in not writeoff and not selled!'
                ))
