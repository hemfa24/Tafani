from odoo import api, fields, models, tools, _
from docutils.nodes import field
from odoo.exceptions import ValidationError, Warning
import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _default_commssion_rule(self):
        default_sale_commission = self.env['sale.commission']
        if self.sale_commission_id:
            return default_sale_commission
        return super(AccountInvoice, self)._default_commssion_rule()

    def button_draft(self):
        res = super(AccountInvoice, self).button_draft()
        for move in self:
            if move.commission_id:
                move.commission_id.unlink()
        return res


    # Removed Below methods due to revert credit note's commission calc postponed by phone call meeting on 18 Apr 24
    # def get_categ_commission(self, commission_brw, invoice):
    #     if invoice.move_type != 'out_refund':
    #         return super(AccountInvoice, self).get_categ_commission(commission_brw, invoice)
    #     else:
    #         if invoice.reversed_entry_id and invoice.reversed_entry_id.commission_id:
    #             exception_obj = self.env['sale.commission.exception']
    #             invoice_commission_obj = self.env['sale.commission.lines']
    #             invoice_commission_ids = []
    #             for line in invoice.invoice_line_ids:
    #                 if not line.product_id:
    #                     continue
    #                 invoice_commission_data = {}
    #                 exception_ids = []
    #                 if invoice.move_type == 'out_refund':
    #                     amount = line.price_subtotal * -1
    #                 else:
    #                     amount = line.price_subtotal * -1
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
    #                                 invoice_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'categ_id': categ_id.id,
    #                                                            'user_id': invoice.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                             else:
    #                                 invoice_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': product_id.id,
    #                                                            'user_id': invoice.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                             invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
    #                         else:
    #                             sales_team = invoice.sale_commission_id.sales_team.filtered(
    #                                 lambda x: x == invoice.team_id)
    #                             if sales_team.team_manager and sales_team.manager_percentage:
    #                                 manager_commission_amount = amount * (sales_team.manager_percentage / 100)
    #                                 if exception.based_on == "product_categories":
    #                                     name = 'Commission Exception for Product Category' + tools.ustr(
    #                                         categ_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.manager_percentage) + '%' + ' For Manager'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': sales_team.team_manager.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'categ_id': categ_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': manager_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                 else:
    #                                     name = 'Commission Exception for Product' + tools.ustr(
    #                                         exception.product_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.manager_percentage) + '%' + ' For Manager'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': sales_team.team_manager.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': manager_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                 invoice_commission_ids.append(
    #                                     invoice_commission_obj.create(invoice_commission_data))
    #
    #                             if sales_team.user_id and sales_team.percentage:
    #                                 team_manager_commission_amount = amount * (sales_team.percentage / 100)
    #                                 if exception.based_on == "product_categories":
    #                                     name = 'Commission Exception for Product Category' + tools.ustr(
    #                                         categ_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.percentage) + '%' + ' For Team Leader'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': sales_team.user_id.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'categ_id': categ_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': team_manager_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                 else:
    #                                     name = 'Commission Exception for Product' + tools.ustr(
    #                                         exception.product_id.name) + '" of ' + tools.ustr(
    #                                         sales_team.percentage) + '%' + ' For Team Leader'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': sales_team.user_id.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'commission_amount': team_manager_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                 invoice_commission_ids.append(
    #                                     invoice_commission_obj.create(invoice_commission_data))
    #
    #                             if sales_team.normal_user_ids and sales_team.members_percentage:
    #                                 for users in sales_team.normal_user_ids:
    #                                     members_percentage_commission_amount = amount * (
    #                                             sales_team.members_percentage / 100)
    #                                     if exception.based_on == "product_categories":
    #                                         name = 'Commission Exception for Product Category' + tools.ustr(
    #                                             categ_id.name) + '" of ' + tools.ustr(
    #                                             sales_team.members_percentage) + '%' + ' For Member'
    #                                         invoice_commission_data = {'name': name,
    #                                                                    'user_id': users.id,
    #                                                                    'team_id': sales_team.id,
    #                                                                    'partner_id': invoice.partner_id.id,
    #                                                                    'commission_id': commission_brw.id,
    #                                                                    'categ_id': categ_id.id,
    #                                                                    'type_name': commission_brw.name,
    #                                                                    'comm_type': commission_brw.comm_type,
    #                                                                    'commission_amount': members_percentage_commission_amount,
    #                                                                    'invoice_id': invoice.id,
    #                                                                    'date': datetime.datetime.today()}
    #                                         invoice_commission_ids.append(
    #                                             invoice_commission_obj.create(invoice_commission_data))
    #                                     else:
    #                                         name = 'Commission Exception for Product' + tools.ustr(
    #                                             exception.product_id.name) + '" of ' + tools.ustr(
    #                                             sales_team.members_percentage) + '%' + ' For Member'
    #                                         invoice_commission_data = {'name': name,
    #                                                                    'user_id': users.id,
    #                                                                    'team_id': sales_team.id,
    #                                                                    'partner_id': invoice.partner_id.id,
    #                                                                    'commission_id': commission_brw.id,
    #                                                                    'product_id': product_id.id,
    #                                                                    'type_name': commission_brw.name,
    #                                                                    'comm_type': commission_brw.comm_type,
    #                                                                    'commission_amount': members_percentage_commission_amount,
    #                                                                    'invoice_id': invoice.id,
    #                                                                    'date': datetime.datetime.today()}
    #                                         invoice_commission_ids.append(
    #                                             invoice_commission_obj.create(invoice_commission_data))
    #                     else:
    #                         for agents in self.agents_ids:
    #                             if exception.based_on == "product_categories":
    #                                 invoice_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'categ_id': categ_id.id,
    #                                                            'agents': agents.id,
    #                                                            'user_id': invoice.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                             else:
    #                                 invoice_commission_data = {'name': name,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': product_id.id,
    #                                                            'agents': agents.id,
    #                                                            'user_id': invoice.user_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'commission_amount': product_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                             invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
    #             return invoice_commission_ids
    #     return []
    #
    # def get_partner_commission(self, commission_brw, invoice):
    #     if invoice.move_type != 'out_refund':
    #         return super(AccountInvoice, self).get_partner_commission(commission_brw, invoice)
    #     else:
    #         if invoice.reversed_entry_id and invoice.reversed_entry_id.commission_id:
    #             invoice_commission_ids = []
    #             invoice_commission_obj = self.env['sale.commission.lines']
    #             sales_person_list = commission_brw.user_ids
    #             for line in invoice.invoice_line_ids:
    #                 if invoice.move_type == 'out_refund':
    #                     amount = line.price_subtotal * -1
    #                 else:
    #                     amount = line.price_subtotal * -1
    #                 name = ''
    #                 invoice_commission_data = {}
    #                 affiliated_commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
    #                 non_affiliated_commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
    #                 if commission_brw.compute_for in ('sales_person', 'sales_team'):
    #                     if commission_brw.compute_for == 'sales_person':
    #                         print("You are in sales person")
    #                         if (
    #                                 invoice.user_id and invoice.user_id in sales_person_list) and invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             invoice_commission_data = {'name': name,
    #                                                        'user_id': invoice.user_id.id,
    #                                                        'partner_id': invoice.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Affiliated Partner',
    #                                                        'commission_amount': affiliated_commission_amount,
    #                                                        'invoice_id': invoice.id,
    #                                                        'date': datetime.datetime.today()}
    #                         elif (
    #                                 invoice.user_id and invoice.user_id in sales_person_list) and not invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             invoice_commission_data = {'name': name,
    #                                                        'user_id': invoice.user_id.id,
    #                                                        'partner_id': invoice.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Non-Affiliated Partner',
    #                                                        'commission_amount': non_affiliated_commission_amount,
    #                                                        'invoice_id': invoice.id,
    #                                                        'date': datetime.datetime.today()}
    #                         if invoice_commission_data:
    #                             invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
    #                     else:
    #                         sales_team = invoice.sale_commission_id.sales_team.filtered(lambda x: x == invoice.team_id)
    #
    #                         if sales_team.team_manager and sales_team.manager_percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 invoice_commission_data = {'name': name,
    #                                                            'user_id': sales_team.team_manager.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': invoice.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Affiliated Partner',
    #                                                            'commission_amount': affiliated_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #
    #                             else:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 invoice_commission_data = {'name': name,
    #                                                            'user_id': sales_team.team_manager.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': invoice.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Non-Affiliated Partner',
    #                                                            'commission_amount': non_affiliated_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                                 if invoice_commission_data:
    #                                     invoice_commission_ids.append(
    #                                         invoice_commission_obj.create(invoice_commission_data))
    #
    #                         if sales_team.user_id and sales_team.percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 invoice_commission_data = {'name': name,
    #                                                            'user_id': sales_team.user_id.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': invoice.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Affiliated Partner',
    #                                                            'commission_amount': affiliated_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #                             else:
    #                                 name = 'Partner commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' (' + tools.ustr(
    #                                     commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                     invoice.partner_id.name) + '"'
    #                                 invoice_commission_data = {'name': name,
    #                                                            'user_id': sales_team.user_id.id,
    #                                                            'team_id': sales_team.id,
    #                                                            'partner_id': invoice.partner_id.id,
    #                                                            'commission_id': commission_brw.id,
    #                                                            'product_id': line.product_id.id,
    #                                                            'type_name': commission_brw.name,
    #                                                            'comm_type': commission_brw.comm_type,
    #                                                            'partner_type': 'Non-Affiliated Partner',
    #                                                            'commission_amount': non_affiliated_commission_amount,
    #                                                            'invoice_id': invoice.id,
    #                                                            'date': datetime.datetime.today()}
    #
    #                             if invoice_commission_data:
    #                                 invoice_commission_ids.append(
    #                                     invoice_commission_obj.create(invoice_commission_data))
    #
    #                         if sales_team.normal_user_ids and sales_team.members_percentage:
    #                             if invoice.partner_id.is_affiliated:
    #                                 for users in sales_team.normal_user_ids:
    #                                     name = 'Partner commission " ' + tools.ustr(
    #                                         commission_brw.name) + ' (' + tools.ustr(
    #                                         commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                         invoice.partner_id.name) + '"'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': users.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': line.product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'partner_type': 'Affiliated Partner',
    #                                                                'commission_amount': affiliated_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                     if invoice_commission_data:
    #                                         invoice_commission_ids.append(
    #                                             invoice_commission_obj.create(invoice_commission_data))
    #
    #                             else:
    #                                 for users in sales_team.normal_user_ids:
    #                                     name = 'Partner commission " ' + tools.ustr(
    #                                         commission_brw.name) + ' (' + tools.ustr(
    #                                         commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                         invoice.partner_id.name) + '"'
    #                                     invoice_commission_data = {'name': name,
    #                                                                'user_id': users.id,
    #                                                                'team_id': sales_team.id,
    #                                                                'partner_id': invoice.partner_id.id,
    #                                                                'commission_id': commission_brw.id,
    #                                                                'product_id': line.product_id.id,
    #                                                                'type_name': commission_brw.name,
    #                                                                'comm_type': commission_brw.comm_type,
    #                                                                'partner_type': 'Non-Affiliated Partner',
    #                                                                'commission_amount': non_affiliated_commission_amount,
    #                                                                'invoice_id': invoice.id,
    #                                                                'date': datetime.datetime.today()}
    #                                     if invoice_commission_data:
    #                                         invoice_commission_ids.append(
    #                                             invoice_commission_obj.create(invoice_commission_data))
    #                 else:
    #                     for agents in self.agents_ids:
    #                         if invoice.partner_id.is_affiliated:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             invoice_commission_data = {'name': name,
    #                                                        'user_id': invoice.user_id.id,
    #                                                        'agents': agents.id,
    #                                                        'partner_id': invoice.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Affiliated Partner',
    #                                                        'commission_amount': affiliated_commission_amount,
    #                                                        'invoice_id': invoice.id,
    #                                                        'date': datetime.datetime.today()}
    #                         else:
    #                             name = 'Partner commission " ' + tools.ustr(commission_brw.name) + ' (' + tools.ustr(
    #                                 commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(
    #                                 invoice.partner_id.name) + '"'
    #                             invoice_commission_data = {'name': name,
    #                                                        'user_id': invoice.user_id.id,
    #                                                        'agents': agents.id,
    #                                                        'partner_id': invoice.partner_id.id,
    #                                                        'commission_id': commission_brw.id,
    #                                                        'type_name': commission_brw.name,
    #                                                        'comm_type': commission_brw.comm_type,
    #                                                        'partner_type': 'Non-Affiliated Partner',
    #                                                        'commission_amount': non_affiliated_commission_amount,
    #                                                        'invoice_id': invoice.id,
    #                                                        'date': datetime.datetime.today()}
    #                         if invoice_commission_data:
    #                             invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
    #             return invoice_commission_ids
    #     return []
    #
    # def get_standard_commission(self, commission_brw, invoice):
    #     if invoice.move_type != 'out_refund':
    #         return super(AccountInvoice, self).get_standard_commission(commission_brw, invoice)
    #     else:
    #         if invoice.reversed_entry_id and invoice.reversed_entry_id.commission_id:
    #             invoice_commission_ids = []
    #             invoice_commission_obj = self.env['sale.commission.lines']
    #             for line in invoice.invoice_line_ids:
    #                 if invoice.move_type == 'out_refund':
    #                     amount = line.price_subtotal * -1
    #                 else:
    #                     amount = line.price_subtotal * -1
    #                 name = ''
    #                 if commission_brw.compute_free == 'percentage':
    #                     standard_commission_amount = amount * (commission_brw.standard_commission / 100)
    #                     name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
    #                         commission_brw.standard_commission) + '%)" for product "' + tools.ustr(
    #                         line.product_id.name) + '"'
    #                 else:
    #                     standard_commission_amount = commission_brw.sale_commission
    #                     name = 'Standard commission " ' + tools.ustr(commission_brw.name) + ' ( ' + tools.ustr(
    #                         commission_brw.sale_commission) + ')" for product "' + tools.ustr(
    #                         line.product_id.name) + '"'
    #                 if commission_brw.compute_for in ('sales_person', 'sales_team'):
    #                     if commission_brw.compute_for == 'sales_person':
    #                         standard_invoice_commission_data = {
    #                             'name': name,
    #                             'user_id': invoice.user_id.id,
    #                             'invoice_id': invoice.id,
    #                             'commission_id': commission_brw.id,
    #                             'product_id': line.product_id.id,
    #                             'type_name': commission_brw.name,
    #                             'comm_type': commission_brw.comm_type,
    #                             'commission_amount': standard_commission_amount,
    #                             'date': datetime.datetime.today()}
    #                         invoice_commission_ids.append(
    #                             invoice_commission_obj.create(standard_invoice_commission_data))
    #                     else:
    #                         sales_team = self.sale_commission_id.sales_team.filtered(lambda x: x == self.team_id)
    #                         if sales_team.team_manager and sales_team.manager_percentage:
    #                             manager_commission_amount = amount * (sales_team.manager_percentage / 100)
    #                             name = 'Standard commission " ' + tools.ustr(
    #                                 commission_brw.name) + ' Manager ' + ' ( ' + tools.ustr(
    #                                 sales_team.manager_percentage) + '%)" for product "' + tools.ustr(
    #                                 line.product_id.name) + '"'
    #                             standard_invoice_commission_data = {'name': name,
    #                                                                 'user_id': sales_team.team_manager.id,
    #                                                                 'team_id': sales_team.id,
    #                                                                 'commission_id': commission_brw.id,
    #                                                                 'product_id': line.product_id.id,
    #                                                                 'type_name': commission_brw.name,
    #                                                                 'comm_type': commission_brw.comm_type,
    #                                                                 'invoice_id': invoice.id,
    #                                                                 'commission_amount': manager_commission_amount,
    #                                                                 'date': datetime.datetime.today()}
    #                             invoice_commission_ids.append(
    #                                 invoice_commission_obj.create(standard_invoice_commission_data))
    #                         if sales_team.user_id and sales_team.percentage:
    #                             team_manager_commission_amount = amount * (sales_team.percentage / 100)
    #                             name = 'Standard commission " ' + tools.ustr(
    #                                 commission_brw.name) + ' Team Leader ' + ' ( ' + tools.ustr(
    #                                 sales_team.percentage) + '%)" for product "' + tools.ustr(
    #                                 line.product_id.name) + '"'
    #                             standard_invoice_commission_data = {'name': name,
    #                                                                 'user_id': sales_team.user_id.id,
    #                                                                 'team_id': sales_team.id,
    #                                                                 'commission_id': commission_brw.id,
    #                                                                 'product_id': line.product_id.id,
    #                                                                 'type_name': commission_brw.name,
    #                                                                 'comm_type': commission_brw.comm_type,
    #                                                                 'commission_amount': team_manager_commission_amount,
    #                                                                 'invoice_id': invoice.id,
    #                                                                 'date': datetime.datetime.today()}
    #                             invoice_commission_ids.append(
    #                                 invoice_commission_obj.create(standard_invoice_commission_data))
    #                         if sales_team.normal_user_ids and sales_team.members_percentage:
    #                             members_percentage_commission_amount = amount * (sales_team.members_percentage / 100)
    #                             for users in sales_team.normal_user_ids:
    #                                 name = 'Standard commission " ' + tools.ustr(
    #                                     commission_brw.name) + ' User ' + ' ( ' + tools.ustr(
    #                                     sales_team.members_percentage) + '%)" for product "' + tools.ustr(
    #                                     line.product_id.name) + '"'
    #                                 standard_invoice_commission_data = {'name': name,
    #                                                                     'user_id': users.id,
    #                                                                     'team_id': sales_team.id,
    #                                                                     'commission_id': commission_brw.id,
    #                                                                     'product_id': line.product_id.id,
    #                                                                     'type_name': commission_brw.name,
    #                                                                     'comm_type': commission_brw.comm_type,
    #                                                                     'commission_amount': members_percentage_commission_amount,
    #                                                                     'invoice_id': invoice.id,
    #                                                                     'date': datetime.datetime.today()}
    #                                 invoice_commission_ids.append(
    #                                     invoice_commission_obj.create(standard_invoice_commission_data))
    #                 else:
    #                     for agents in self.agents_ids:
    #                         standard_invoice_commission_data = {
    #                             'name': name,
    #                             'user_id': invoice.user_id.id,
    #                             'agents': agents.id,
    #                             'commission_id': commission_brw.id,
    #                             'product_id': line.product_id.id,
    #                             'type_name': commission_brw.name,
    #                             'comm_type': commission_brw.comm_type,
    #                             'commission_amount': standard_commission_amount,
    #                             'invoice_id': invoice.id,
    #                             'date': datetime.datetime.today()
    #                         }
    #                         invoice_commission_ids.append(
    #                             invoice_commission_obj.create(standard_invoice_commission_data))
    #             return invoice_commission_ids
    #     return []
