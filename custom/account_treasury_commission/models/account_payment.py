# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.exceptions import ValidationError
import datetime


class accountPayment(models.Model):
    _inherit = "account.payment"

    is_create_payment_commission = fields.Boolean(
        'Create Payment Commission',
        copy=False,
    )
    commission_ids = fields.One2many(
        'sale.commission.lines',
        'payment_id',
        string='Sales Commissions',
        help="Sale Commission related to this invoice(based on sales person)"
    )
    commission_m2m_ids = fields.Many2many(
        'sale.commission.lines',
        string='Sales Commission',
    )
    is_invoice_checked_with_commission = fields.Boolean(
        'Checked Invoice with commission',
        compute='_compute_invoice_checked_wth_comm',
        store=True
    )

    @api.onchange("sale_commission_id")
    def _compute_for_agents(self):
        if self.sale_commission_id:
            agents = self.sale_commission_id.agents
            self.agents_ids = agents.ids
            return {
                "domain": {
                    "agents_ids": [("id", "in", self.agents_ids.ids)]
                }
            }

    def act_payment_views(self, name, payment_type, partner_type, journal_type):
        action = super(accountPayment, self).act_payment_views(name, payment_type, partner_type, journal_type)
        action['context']['default_is_create_payment_commission'] = True
        print("@@@@@@@@@@@@@@@@@@@@action", action)
        return action

    @api.depends('move_ids', 'move_ids.check')
    def _compute_invoice_checked_wth_comm(self):
        for rec in self:
            if any(move.check for move in rec.move_ids):
                rec.is_invoice_checked_with_commission = True
            else:
                rec.is_invoice_checked_with_commission = False

    # @api.onchange('cheque_operation_ids', 'move_ids')
    # def onchange_set_amount(self):
    #     super(accountPayment, self).onchange_set_amount()
    #     for payment in self:
    #         payment.is_invoice_checked_with_commission = True

    # [25 Apr 24] Comment this cause called js_assign_outstanding_line from hemfa_Account_treasury module and
    # handled commission from js_assign_outstanding_line[account_move file] in module account_treasury_commission
    # def action_post(self):
    #     res = super(accountPayment, self).action_post()
    #     commission_configuration = self.env.user.company_id.commission_configuration
    #     if commission_configuration == 'payment':
    #         payments_for_commission = self.filtered(lambda pay: pay.is_create_payment_commission)
    #         payments_for_commission.get_treasury_payment_commission()
    #     return res

    def action_draft(self):
        if any(commision.invoiced for commision in self.commission_m2m_ids):
            raise ValidationError(
                _("Sorry, The payment's commission is already billed you are not allowed to reset this Payment."))
        self.commission_m2m_ids.unlink()
        res = super(accountPayment, self).action_draft()
        return res

    def get_treasury_payment_commission(self, outstanging_inv_ids=None):
        payment_commission_ids = []
        for payment in self:
            if payment.payment_type != 'inbound':
                continue
            invoice_commission_ids = []
            invoice_ids = outstanging_inv_ids or payment.move_ids.filtered(lambda pay: pay.check)
            inv_total_amount = sum(invoice_ids.mapped('amount_total'))
            # if payment.amount < inv_total_amount:
            #     continue
            for invoice in invoice_ids.with_context(default_partner_type=False):
                if invoice.amount_residual != 0.0:
                    continue
                commission_obj = self.env['sale.commission']
                commission_id = self.env['sale.commission']
                if invoice.sale_commission_id:
                    commission_id = invoice.sale_commission_id

                    if invoice.sale_commission_id.compute_for == 'sales_person':
                        if invoice.user_id not in invoice.sale_commission_id.user_ids:
                            return False

                    if invoice.sale_commission_id.compute_for == 'sales_team':
                        if invoice.team_id not in invoice.sale_commission_id.sales_team:
                            return False

                    if invoice.sale_commission_id.compute_for == 'agents' and not invoice.agents_ids:
                        return False

                if not commission_id:
                    return False

                if commission_id.comm_type == 'categ':
                    invoice_commission_ids = invoice.get_categ_commission(commission_id, invoice)
                elif commission_id.comm_type == 'partner':
                    invoice_commission_ids = invoice.get_partner_commission(commission_id, invoice)
                elif commission_id.comm_type == 'product':
                    invoice_commission_ids = invoice.get_categ_commission(commission_id, invoice)
                else:
                    invoice_commission_ids = invoice.get_standard_commission(commission_id, invoice)
                invoice_commission_m2m_ids = self.env['sale.commission.lines']
                for inv_comm_id in invoice_commission_ids:
                    invoice_commission_m2m_ids += inv_comm_id
                #     inv_comm_id.write({
                #         'payment_id': payment.id
                #     })
                # name = "move_ids"
                # string = "Operations"
                # domain = "[('partner_id','=',partner_id),('move_type', '=', 'out_invoice'),('payment_state','!=','paid'),]"
                payment_ids = self.env['account.payment'].search(
                    [('move_ids.check', '=', True), ('move_ids', 'in', [invoice.id])])
                print("!!!!!!!!payment_ids!!!!!!!!!!!1", payment_ids)
                # print(opllll)
                print("@@@@@@@@@@@@@@invoice_commission_ids", invoice_commission_m2m_ids)
                invoice_commission_m2m_ids.write({
                    'payment_ids': [(6, 0, payment_ids.ids)]
                })
                for payment in payment_ids:
                    payment.write({
                        'commission_m2m_ids': [(6, 0, invoice_commission_m2m_ids.ids)]
                    })
            return invoice_commission_ids
            # for invoice in self:
            #     commission_obj = self.env['sale.commission']
            #     commission_id = self.env['sale.commission']
            #     if payment.sale_commission_id:
            #         commission_id = payment.sale_commission_id
            #
            #         if payment.sale_commission_id.compute_for == 'sales_person':
            #             if payment.salesperson_id not in payment.sale_commission_id.user_ids:
            #                 return False
            #
            #         if payment.sale_commission_id.compute_for == 'sales_team':
            #             if payment.team_id not in payment.sale_commission_id.sales_team:
            #                 return False
            #
            #         if payment.sale_commission_id.compute_for == 'agents' and not payment.agents_ids:
            #             return False
            #
            #     if not commission_id:
            #         return False
            #
            #     if commission_id.comm_type == 'normal':
            #         payment_commission_ids = self.get_payment_standard_commission(commission_id, payment)
            #     elif commission_id.comm_type == 'categ':
            #         payment_commission_ids = self.get_payment_product_commission(commission_id, payment, invoice)
            #     elif commission_id.comm_type == 'product':
            #         payment_commission_ids = self.get_payment_product_commission(commission_id, payment, invoice)
            #     elif commission_id.comm_type == 'partner':
            #         payment_commission_ids = self.get_payment_partner_commission(commission_id, payment, invoice)

            return payment_commission_ids

    # ============================================================================================

    # def get_payment_standard_commission(self, commission_brw, payment):
    #     payment_commission_ids = []
    #     payment_commission_obj = self.env['sale.commission.lines']
    #     for move in payment.move_ids.filtered(lambda move: move.check and move.payment_state == 'paid'):
    #         if move.check:
    #             for line in move.invoice_line_ids:
    #                 # amount = payment.amount
    #                 amount = line.price_subtotal
    #                 name = ''
    #                 if commission_brw.compute_free == 'percentage':
    #                     standard_commission_amount = amount * (commission_brw.standard_commission / 100)
    #                     name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
    #                         commission_brw.standard_commission) + '%)" for payment "' + tools.ustr(payment.name) + '"'
    #                 else:
    #                     standard_commission_amount = commission_brw.sale_commission
    #                     name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
    #                         commission_brw.sale_commission) + ')" for payment "' + tools.ustr(payment.name) + '"'
    #                 if commission_brw.compute_for in ('sales_person', 'sales_team'):
    #                     if commission_brw.compute_for == 'sales_person':
    #                         standard_payment_commission_data = {
    #                             'name': name,
    #                             'user_id': payment.salesperson_id.id,
    #                             'payment_id': payment.id,
    #                             'invoice_id': move.id,
    #                             'commission_id': commission_brw.id,
    #                             'type_name': commission_brw.name,
    #                             'comm_type': commission_brw.comm_type,
    #                             'commission_amount': standard_commission_amount,
    #                             'date': datetime.datetime.today(),
    #                             'partner_type': False,
    #                         }
    #                         payment_commission_ids.append(
    #                             payment_commission_obj.with_context(default_partner_type=False).create(
    #                                 standard_payment_commission_data))
    #                     else:
    #                         sales_team = payment.sale_commission_id.sales_team.filtered(lambda x: x == move.team_id)
    #                         if sales_team.team_manager and sales_team.manager_percentage:
    #                             manager_commission_amount = amount * (sales_team.manager_percentage / 100)
    #                             name = 'Standard commission " ' + tools.ustr(
    #                                 commission_brw.name) + ' Manager ' + ' ( ' + tools.ustr(
    #                                 sales_team.manager_percentage) + '%)" for product "' + tools.ustr(
    #                                 line.product_id.name) + '"'
    #                             standard_payment_commission_data = {'name': name,
    #                                                                 'user_id': sales_team.team_manager.id,
    #                                                                 'team_id': sales_team.id,
    #                                                                 'commission_id': commission_brw.id,
    #                                                                 'product_id': line.product_id.id,
    #                                                                 'type_name': commission_brw.name,
    #                                                                 'comm_type': commission_brw.comm_type,
    #                                                                 'payment_id': payment.id,
    #                                                                 'invoice_id': move.id,
    #                                                                 'commission_amount': manager_commission_amount,
    #                                                                 'date': datetime.datetime.today(),
    #                                                                 'partner_type': False, }
    #                             payment_commission_ids.append(
    #                                 payment_commission_obj.create(standard_payment_commission_data))
    #                         if sales_team.user_id and sales_team.percentage:
    #                             team_manager_commission_amount = amount * (sales_team.percentage / 100)
    #                             name = 'Standard commission " ' + tools.ustr(
    #                                 commission_brw.name) + ' Team Leader ' + ' ( ' + tools.ustr(
    #                                 sales_team.percentage) + '%)" for product "' + tools.ustr(
    #                                 line.product_id.name) + '"'
    #                             standard_payment_commission_data = {'name': name,
    #                                                                 'user_id': sales_team.user_id.id,
    #                                                                 'team_id': sales_team.id,
    #                                                                 'commission_id': commission_brw.id,
    #                                                                 'product_id': line.product_id.id,
    #                                                                 'type_name': commission_brw.name,
    #                                                                 'comm_type': commission_brw.comm_type,
    #                                                                 'commission_amount': team_manager_commission_amount,
    #                                                                 'payment_id': payment.id,
    #                                                                 'invoice_id': move.id,
    #                                                                 'date': datetime.datetime.today(),
    #                                                                 'partner_type': False, }
    #                             payment_commission_ids.append(
    #                                 payment_commission_obj.create(standard_payment_commission_data))
    #                         if sales_team.normal_user_ids and sales_team.members_percentage:
    #                             members_percentage_commission_amount = amount * (sales_team.members_percentage / 100)
    #                             for users in sales_team.normal_user_ids:
    #                                 name = 'Standard commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' User ' + ' ( ' + tools.ustr(
    #                                     sales_team.members_percentage) + '%)" for product "' + tools.ustr(
    #                                     line.product_id.name) + '"'
    #                                 standard_payment_commission_data = {'name': name,
    #                                                                     'user_id': users.id,
    #                                                                     'team_id': sales_team.id,
    #                                                                     'commission_id': commission_brw.id,
    #                                                                     'product_id': line.product_id.id,
    #                                                                     'type_name': commission_brw.name,
    #                                                                     'comm_type': commission_brw.comm_type,
    #                                                                     'commission_amount': members_percentage_commission_amount,
    #                                                                     'payment_id': payment.id,
    #                                                                     'invoice_id': move.id,
    #                                                                     'date': datetime.datetime.today(),
    #                                                                     'partner_type': False, }
    #                                 payment_commission_ids.append(
    #                                     payment_commission_obj.create(standard_payment_commission_data))
    #                 else:
    #                     for agents in payment.agents_ids:
    #                         standard_payment_commission_data = {
    #                             'name': name,
    #                             'user_id': payment.user_id.id,
    #                             'agents': agents.id,
    #                             'commission_id': commission_brw.id,
    #                             'product_id': line.product_id.id,
    #                             'type_name': commission_brw.name,
    #                             'comm_type': commission_brw.comm_type,
    #                             'commission_amount': standard_commission_amount,
    #                             'payment_id': payment.id,
    #                             'invoice_id': move.id,
    #                             'date': datetime.datetime.today(),
    #                             'partner_type': False,
    #                         }
    #                         payment_commission_ids.append(
    #                             payment_commission_obj.create(standard_payment_commission_data))
    #     return payment_commission_ids

    # ============================================================================================

    def get_exceptions(self, line, commission_brw):
        exception_obj = self.env['sale.commission.exception']
        categ_obj = self.env['product.category']

        if commission_brw.comm_type == 'product':
            product_exception_id = exception_obj.search([
                ('product_id', '=', line.product_id.id),
                ('commission_id', '=', commission_brw.id),
                ('based_on', '=', 'products')])
            if product_exception_id:
                return product_exception_id

        if commission_brw.comm_type == 'categ':
            exclusive_categ_exception_id = exception_obj.search([
                ('categ_id', '=', line.product_id.categ_id.id),
                ('commission_id', '=', commission_brw.id),
                ('based_on', '=', 'product_categories'), ])
            if exclusive_categ_exception_id:
                return exclusive_categ_exception_id
        return []

    # ============================================================================================

    # def get_payment_product_commission(self, commission_brw, payment, invoice):
    #     exception_obj = self.env['sale.commission.exception']
    #     payment_commission_obj = self.env['sale.commission.lines']
    #     payment_commission_ids = []
    #     for move in payment.move_ids.filtered(lambda move: move.check and move.payment_state == 'paid'):
    #         if move.check:
    #             for line in move.invoice_line_ids:
    #                 if not line.product_id:
    #                     continue
    #                 payment_commission_data = {}
    #                 exception_ids = []
    #                 amount = line.price_subtotal
    #
    #                 exception_ids = self.get_exceptions(line, commission_brw)
    #                 for exception in exception_ids:
    #                     product_id = False
    #                     categ_id = False
    #                     name = ''
    #
    #                     if commission_brw.compute_free == 'percentage':
    #                         product_commission_amount = amount * (commission_brw.standard_commission / 100)
    #                     else:
    #                         product_commission_amount = commission_brw.sale_commission
    #
    #                     if exception.based_on == "product_categories":
    #                         categ_id = exception.categ_id
    #                         if commission_brw.compute_free == 'percentage':
    #                             name = 'Commission Exception for Product Category ' + tools.ustr(
    #                                 categ_id.name) + '" of ' + tools.ustr(commission_brw.standard_commission) + '%'
    #                         else:
    #                             product_commission_amount = commission_brw.sale_commission
    #                             name = 'Commission Exception for Product Category ' + tools.ustr(
    #                                 categ_id.name) + '" of Fix ' + tools.ustr(commission_brw.sale_commission)
    #                     else:
    #                         product_id = exception.product_id
    #                         if commission_brw.compute_free == 'percentage':
    #                             name = 'Commission Exception for Product ' + tools.ustr(
    #                                 exception.product_id.name) + '" of ' + tools.ustr(
    #                                 commission_brw.standard_commission) + '%'
    #                         else:
    #                             product_commission_amount = commission_brw.sale_commission
    #                             name = 'Commission Exception for Product ' + tools.ustr(
    #                                 exception.product_id.name) + '" of Fix ' + tools.ustr(
    #                                 commission_brw.sale_commission)
    #
    #                     if commission_brw.compute_for in ('sales_person', 'sales_team'):
    #                         if commission_brw.compute_for == 'sales_person':
    #                             if exception.based_on == "product_categories":
    #                                 payment_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'categ_id': categ_id.id,
    #                                                            'user_id': payment.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': move.id,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today(),
    #                                                            'partner_type': False}
    #                             else:
    #                                 payment_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': product_id.id,
    #                                                            'user_id': payment.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': move.id,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today(),
    #                                                            'partner_type': False}
    #                             payment_commission_ids.append(payment_commission_obj.create(payment_commission_data))
    #                         else:
    #                             sales_team = invoice.sale_commission_id.sales_team.filtered(
    #                                 lambda x: x == invoice.team_id)
    #                             if sales_team.team_manager and sales_team.manager_percentage:
    #                                 manager_commission_amount = amount * (sales_team.manager_percentage / 100)
    #                                 if exception.based_on == "product_categories":
    #                                     name = 'Commission Exception for Product Category' + tools.ustr(
    #                                         categ_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.manager_percentage) + '%' + ' For Manager'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': sales_team.team_manager.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'categ_id': categ_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': manager_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today(),
    #                                                                'partner_type': False}
    #                                 else:
    #                                     name = 'Commission Exception for Product' + tools.ustr(
    #                                         exception.product_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.manager_percentage) + '%' + ' For Manager'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': sales_team.team_manager.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': manager_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today(),
    #                                                                'partner_type': False}
    #                                 payment_commission_ids.append(
    #                                     payment_commission_obj.create(payment_commission_data))
    #
    #                             if sales_team.user_id and sales_team.percentage:
    #                                 team_manager_commission_amount = amount * (sales_team.percentage / 100)
    #                                 if exception.based_on == "product_categories":
    #                                     name = 'Commission Exception for Product Category' + tools.ustr(
    #                                         categ_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.percentage) + '%' + ' For Team Leader'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': sales_team.user_id.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'categ_id': categ_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': team_manager_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today(),
    #                                                                'partner_type': False}
    #                                 else:
    #                                     name = 'Commission Exception for Product' + tools.ustr(
    #                                         exception.product_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.percentage) + '%' + ' For Team Leader'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': sales_team.user_id.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': team_manager_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today(),
    #                                                                'partner_type': False}
    #                                 payment_commission_ids.append(
    #                                     payment_commission_obj.create(payment_commission_data))
    #
    #                             if sales_team.normal_user_ids and sales_team.members_percentage:
    #                                 for users in sales_team.normal_user_ids:
    #                                     members_percentage_commission_amount = amount * (
    #                                             sales_team.members_percentage / 100)
    #                                     if exception.based_on == "product_categories":
    #                                         name = 'Commission Exception for Product Category' + tools.ustr(
    #                                             categ_id.name) + '" of ' + tools.ustr(
    #                                             sales_team.members_percentage) + '%' + ' For Member'
    #                                         payment_commission_data = {'name': name,
    #                                                                    'user_id': users.id,
    #                                                                    'team_id': sales_team.id,
    #                                                                    'partner_id': payment.partner_id.id,
    #                                                                    'commission_id': commission_brw.id,
    #                                                                    'categ_id': categ_id.id,
    #                                                                    'type_name': commission_brw.name,
    #                                                                    'comm_type': commission_brw.comm_type,
    #                                                                    'commission_amount': members_percentage_commission_amount,
    #                                                                    'payment_id': payment.id,
    #                                                                    'date': datetime.datetime.today(),
    #                                                                    'partner_type': False}
    #                                         payment_commission_ids.append(
    #                                             payment_commission_obj.create(payment_commission_data))
    #                                     else:
    #                                         name = 'Commission Exception for Product' + tools.ustr(
    #                                             exception.product_id.name) + '" of ' + tools.ustr(
    #                                             sales_team.members_percentage) + '%' + ' For Member'
    #                                         payment_commission_data = {'name': name,
    #                                                                    'user_id': users.id,
    #                                                                    'team_id': sales_team.id,
    #                                                                    'partner_id': payment.partner_id.id,
    #                                                                    'commission_id': commission_brw.id,
    #                                                                    'product_id': product_id.id,
    #                                                                    'type_name': commission_brw.name,
    #                                                                    'comm_type': commission_brw.comm_type,
    #                                                                    'commission_amount': members_percentage_commission_amount,
    #                                                                    'payment_id': payment.id,
    #                                                                    'date': datetime.datetime.today(),
    #                                                                    'partner_type': False}
    #                                         payment_commission_ids.append(
    #                                             payment_commission_obj.create(payment_commission_data))
    #
    #                     else:
    #                         for agents in payment.agents_ids:
    #                             if exception.based_on == "product_categories":
    #                                 payment_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'categ_id': categ_id.id,
    #                                                            'agents': agents.id,
    #                                                            'user_id': payment.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today(),
    #                                                            'partner_type': False}
    #                             else:
    #                                 payment_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': product_id.id,
    #                                                            'agents': agents.id,
    #                                                            'user_id': payment.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today(),
    #                                                            'partner_type': False}
    #                             payment_commission_ids.append(payment_commission_obj.create(payment_commission_data))
    #     return payment_commission_ids

    # ============================================================================================

    # def get_payment_partner_commission(self, commission_brw, invoice, payment):
    #     payment_commission_ids = []
    #     payment_commission_obj = self.env['sale.commission.lines']
    #     sales_person_list = commission_brw.user_ids
    #     for move in payment.move_ids.filtered(lambda move: move.check and move.payment_state == 'paid'):
    #         if move.check:
    #             for line in move.invoice_line_ids:
    #                 # amount = line.price_subtotal
    #                 name = ''
    #                 # amount = payment.amount
    #                 amount = line.price_subtotal
    #                 payment_commission_data = {}
    #
    #                 affiliated_commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
    #                 non_affiliated_commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
    #                 if commission_brw.compute_for in ('sales_person', 'sales_team'):
    #                     if commission_brw.compute_for == 'sales_person':
    #                         if (
    #                                 invoice.user_id and invoice.user_id in sales_person_list) and invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             payment_commission_data = {'name': name,
    #                                                        'user_id': payment.user_id.id,
    #                                                        'partner_id': payment.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Affiliated Partner',
    #                                                        'commission_amount': affiliated_commission_amount,
    #                                                        'payment_id': payment.id,
    #                                                        'date': datetime.datetime.today()}
    #                         elif (
    #                                 invoice.user_id and invoice.user_id in sales_person_list) and not invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             payment_commission_data = {'name': name,
    #                                                        'user_id': payment.user_id.id,
    #                                                        'partner_id': payment.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Non-Affiliated Partner',
    #                                                        'commission_amount': non_affiliated_commission_amount,
    #                                                        'payment_id': payment.id,
    #                                                        'date': datetime.datetime.today()}
    #                         if payment_commission_data:
    #                             payment_commission_ids.append(payment_commission_obj.create(payment_commission_data))
    #                     else:
    #                         sales_team = invoice.sale_commission_id.sales_team.filtered(lambda x: x == invoice.team_id)
    #
    #                         if sales_team.team_manager and sales_team.manager_percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 payment_commission_data = {'name': name,
    #                                                            'user_id': sales_team.team_manager.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': payment.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Affiliated Partner',
    #                                                            'commission_amount': affiliated_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today()}
    #                             else:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 payment_commission_data = {'name': name,
    #                                                            'user_id': sales_team.team_manager.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': payment.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Non-Affiliated Partner',
    #                                                            'commission_amount': non_affiliated_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today()}
    #                                 if payment_commission_data:
    #                                     payment_commission_ids.append(
    #                                         payment_commission_obj.create(payment_commission_data))
    #
    #                         if sales_team.user_id and sales_team.percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 payment_commission_data = {'name': name,
    #                                                            'user_id': sales_team.user_id.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': payment.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Affiliated Partner',
    #                                                            'commission_amount': affiliated_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today()}
    #
    #                             else:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 payment_commission_data = {'name': name,
    #                                                            'user_id': sales_team.user_id.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': payment.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Non-Affiliated Partner',
    #                                                            'commission_amount': non_affiliated_commission_amount,
    #                                                            'payment_id': payment.id,
    #                                                            'date': datetime.datetime.today()}
    #                             if payment_commission_data:
    #                                 payment_commission_ids.append(
    #                                     payment_commission_obj.create(payment_commission_data))
    #
    #                         if sales_team.normal_user_ids and sales_team.members_percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 for users in sales_team.normal_user_ids:
    #                                     name = 'Partner commission " ' + tools.ustr(
    #                                         commission_brw.name) + ' (' + tools.ustr(
    #                                         commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                         invoice.partner_id.name) + '"'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': users.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': line.product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'partner_type': 'Affiliated Partner',
    #                                                                'commission_amount': affiliated_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today()}
    #                                     if payment_commission_data:
    #                                         payment_commission_ids.append(
    #                                             payment_commission_obj.create(payment_commission_data))
    #
    #                             else:
    #                                 for users in sales_team.normal_user_ids:
    #                                     name = 'Partner commission " ' + tools.ustr(
    #                                         commission_brw.name) + ' (' + tools.ustr(
    #                                         commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                         invoice.partner_id.name) + '"'
    #                                     payment_commission_data = {'name': name,
    #                                                                'user_id': users.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': payment.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': line.product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'partner_type': 'Non-Affiliated Partner',
    #                                                                'commission_amount': non_affiliated_commission_amount,
    #                                                                'payment_id': payment.id,
    #                                                                'date': datetime.datetime.today()}
    #                                     if payment_commission_data:
    #                                         payment_commission_ids.append(
    #                                             payment_commission_obj.create(payment_commission_data))
    #                 else:
    #                     for agents in self.agents_ids:
    #                         if invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             payment_commission_data = {'name': name,
    #                                                        'user_id': payment.user_id.id,
    #                                                        'agents': agents.id,
    #                                                        'partner_id': payment.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Affiliated Partner',
    #                                                        'commission_amount': affiliated_commission_amount,
    #                                                        'payment_id': payment.id,
    #                                                        'date': datetime.datetime.today()}
    #                         else:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             payment_commission_data = {'name': name,
    #                                                        'user_id': payment.user_id.id,
    #                                                        'agents': agents.id,
    #                                                        'partner_id': payment.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Non-Affiliated Partner',
    #                                                        'commission_amount': non_affiliated_commission_amount,
    #                                                        'payment_id': payment.id,
    #                                                        'date': datetime.datetime.today()}
    #                         if payment_commission_data:
    #                             payment_commission_ids.append(payment_commission_obj.create(payment_commission_data))
    #     return payment_commission_ids

    # ============================================================================================
