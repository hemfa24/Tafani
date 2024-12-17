# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError, AccessError


class SaleCommission(models.Model):
    _inherit = 'sale.commission'

    # Remove restriction for multi sales commission rules MEET #30DEC23
    @api.constrains('compute_for')
    def _check_commpute_type(self):
        return True


class SaleCommissionlines(models.Model):
    _inherit = 'sale.commission.lines'

    payment_id = fields.Many2one(
        'account.payment',
        string='Payment Reference',
        copy=False,
    )
    payment_ids = fields.Many2many(
        'account.payment',
        string='Payment Reference',
        copy=False,
    )
    commission_bill_id = fields.Many2one(
        'account.move',
        string='Bill',
        copy=False
    )


class CreateCommisionInvoice(models.Model):
    _inherit = 'create.invoice.commission'

    def invoice_create(self):
        sale_invoice_ids = self.env['sale.commission.lines'].browse(self._context.get('active_ids'))

        if any(line.invoiced for line in sale_invoice_ids):
            raise ValidationError('Invoiced lines cannot be invoiced again.')

        commission_discount_account = self.env.user.company_id.commission_discount_account
        if not commission_discount_account:
            raise ValidationError('You have not configured commission account in sale configuration')

        journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        if not journal:
            raise ValidationError(_('Please define purchase type journal in acccountig for the company %s (%s).',
                                    self.env.company_id.name, self.env.company_id.id))

        commission_in_lst = []
        if self.group_by:
            sale_line_list = []
            agent_line_list = []
            sales_group_dict = {}
            agent_group_dict = {}

            fil_agents = sale_invoice_ids.filtered(lambda x: x.commission_id.compute_for in ('agents'))

            if any(line.agents != fil_agents[0].agents for line in fil_agents):
                raise ValidationError('Please create bill for same agents only')

            for record in fil_agents:
                agent_group_dict.setdefault(record.agents, []).append(record)

            fil_sales = sale_invoice_ids.filtered(
                lambda x: x.commission_id.compute_for in ('sales_person', 'sales_team'))

            if any(line.user_id != fil_sales[0].user_id for line in fil_sales):
                raise ValidationError('Please create bill for same salesperson only')

            for record in fil_sales:
                sales_group_dict.setdefault(record.user_id, []).append(record)

            for dict_record in sales_group_dict:
                partner = self.env['res.partner'].search([('id', '=', dict_record.partner_id.id)], limit=1)
                commission_lines = self.env['sale.commission.lines']
                for inv_record in sales_group_dict.get(dict_record):
                    sale_line_list.append((0, 0, {
                        'name': inv_record.name,
                        'account_id': commission_discount_account.id,
                        'quantity': 1,
                        'price_unit': inv_record.commission_amount,
                    }))
                    commission_lines += inv_record
                inv_id = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'journal_id': journal.id,
                    'invoice_date': self.date if self.date else datetime.datetime.today().date(),
                    'invoice_line_ids': sale_line_list,
                    'commission': True
                })
                commission_lines.write({'commission_bill_id': inv_id.id})

            for dict_record in agent_group_dict:
                partner = self.env['res.partner'].search([('id', '=', dict_record.id)], limit=1)
                commission_lines = self.env['sale.commission.lines']
                for inv_record in agent_group_dict.get(dict_record):
                    commission_lines += inv_record
                    agent_line_list.append((0, 0, {
                        'name': inv_record.name,
                        'account_id': commission_discount_account.id,
                        'quantity': 1,
                        'price_unit': inv_record.commission_amount,
                    }))
                inv_id = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'journal_id': journal.id,
                    'invoice_date': self.date if self.date else datetime.datetime.today().date(),
                    'invoice_line_ids': agent_line_list,
                    'commission': True
                })
                commission_lines.write({'commission_bill_id': inv_id.id})

        else:
            for commission_record in sale_invoice_ids:
                inv_id = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': commission_record.user_id.partner_id.id,
                    'journal_id': journal.id,
                    'invoice_date': self.date if self.date else datetime.datetime.today().date()
                })
                commission_record.write({'commission_bill_id': inv_id.id})
                inv_line_id = self.env['account.move.line'].create({
                    'name': commission_record.name,
                    'account_id': commission_discount_account.id,
                    'quantity': 1,
                    'price_unit': commission_record.commission_amount,
                    'move_id': inv_id.id
                })
        sale_invoice_ids.write({'invoiced': True})
