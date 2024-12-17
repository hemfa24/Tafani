from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError, ValidationError, AccessError
import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _default_commssion_rule(self):
        default_sale_commission = self.env['sale.commission']
        default_commission = default_sale_commission.search([('compute_for', '=', 'sales_person')], limit=1)
        if not default_commission:
            default_commission = default_sale_commission.search([('compute_for', '=', 'sales_team')], limit=1)
        if not default_commission:
            default_commission = default_sale_commission.search([('compute_for', '=', 'agents')], limit=1)
        if default_commission:
            return default_commission.id

    comm_type = fields.Selection(related="sale_commission_id.comm_type", string="Commission Type")
    compute_for = fields.Selection(related="sale_commission_id.compute_for",string="Commission For")
    agents_ids = fields.Many2many("res.partner", string="Agents", domain="[('agent', '=', True)]")
    sale_commission_id = fields.Many2one("sale.commission", string="Commission Rules", default=_default_commssion_rule)
    commission_ids = fields.One2many('sale.commission.lines','order_id', string='Sales Commissions', help="Sale Commission related to this order(based on sales person)")

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

    def get_sales_commission(self):
        for order in self:
            invoice_commission_ids = []
            commission_obj = self.env['sale.commission']
            commission_id = self.env['sale.commission']
            if order.sale_commission_id:
                commission_id = order.sale_commission_id
               
                if order.sale_commission_id.compute_for == 'sales_person':
                    if order.user_id not in order.sale_commission_id.user_ids:
                        return False

                if order.sale_commission_id.compute_for == 'sales_team':
                     if order.team_id not in order.sale_commission_id.sales_team:
                        return False

                if order.sale_commission_id.compute_for == 'agents' and not order.agents_ids:
                    return False

            if not commission_id:
                return False

            if commission_id.comm_type == 'categ':
                invoice_commission_ids = self.get_categ_commission(commission_id, order)
            elif commission_id.comm_type == 'partner':
                invoice_commission_ids = self.get_partner_commission(commission_id, order)
            elif commission_id.comm_type == 'product':
                invoice_commission_ids = self.get_categ_commission(commission_id, order)
            else:
                invoice_commission_ids = self.get_standard_commission(commission_id, order)
        return invoice_commission_ids


    # ==============================================================================================================================
    def get_standard_commission(self, commission_brw, order):
        invoice_commission_ids = []
        invoice_commission_obj = self.env['sale.commission.lines']
        for line in order.order_line:
            amount = line.price_subtotal
            name = ''
            if commission_brw.compute_free == 'percentage':
                standard_commission_amount = amount * (commission_brw.standard_commission / 100)
                name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(commission_brw.standard_commission) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
            else:
                standard_commission_amount = commission_brw.sale_commission
                name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(commission_brw.sale_commission) + ')" for product "' + tools.ustr(line.product_id.name) + '"'
            if commission_brw.compute_for in ('sales_person', 'sales_team'):
                if commission_brw.compute_for == 'sales_person':
                    standard_invoice_commission_data = {'name': name,
                                                   'user_id' : order.user_id.id,
                                                   'commission_id' : commission_brw.id,
                                                   'product_id' : line.product_id.id,
                                                   'type_name' : commission_brw.name,
                                                   'comm_type' : commission_brw.comm_type,
                                                   'commission_amount' : standard_commission_amount,
                                                   'order_id' : order.id,
                                                   'date':datetime.datetime.today()}
                    invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
                else:
                    sales_team = self.sale_commission_id.sales_team.filtered(lambda x: x == self.team_id)
                    if sales_team.team_manager and sales_team.manager_percentage:
                        manager_commission_amount= amount * (sales_team.manager_percentage / 100)
                        name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(sales_team.manager_percentage) + '%)" for product "' + tools.ustr(line.product_id.name) + '"' 
                        standard_invoice_commission_data = {'name': name,
                                                       'user_id' : sales_team.team_manager.id,
                                                       'team_id' : sales_team.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : manager_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
                    if sales_team.user_id and sales_team.percentage:
                        team_manager_commission_amount= amount * (sales_team.percentage / 100)
                        name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(sales_team.percentage) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
                        standard_invoice_commission_data = {'name': name,
                                                       'user_id' : sales_team.user_id.id,
                                                       'team_id' : sales_team.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : team_manager_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
                    if sales_team.normal_user_ids and sales_team.members_percentage:
                        members_percentage_commission_amount= amount * (sales_team.members_percentage / 100)
                        for users in sales_team.normal_user_ids:
                            name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(sales_team.members_percentage) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
                            standard_invoice_commission_data = {'name': name,
                                                           'user_id' : users.id,
                                                           'team_id' : sales_team.id,
                                                           'commission_id' : commission_brw.id,
                                                           'product_id' : line.product_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'commission_amount' : members_percentage_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                            invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
            else:
                for agents in self.agents_ids:
                    standard_invoice_commission_data = {   
                                                        'name': name,
                                                        'user_id' : order.user_id.id,
                                                        'agents' : agents.id,
                                                        'commission_id' : commission_brw.id,
                                                        'product_id' : line.product_id.id,
                                                        'type_name' : commission_brw.name,
                                                        'comm_type' : commission_brw.comm_type,
                                                        'commission_amount' : standard_commission_amount,
                                                        'order_id' : order.id,
                                                        'date':datetime.datetime.today()
                                                        }
                    invoice_commission_ids.append(invoice_commission_obj.create(standard_invoice_commission_data))
        return invoice_commission_ids

    # ========================================================================================================================
    def get_partner_commission(self, commission_brw, order):
        invoice_commission_ids = []
        invoice_commission_obj = self.env['sale.commission.lines']
        sales_person_list = commission_brw.user_ids
        for line in order.order_line:
            amount = line.price_subtotal
            name = ''
            invoice_commission_data = {}
            affiliated_commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
            non_affiliated_commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
            if commission_brw.compute_for in ('sales_person', 'sales_team'):
                if commission_brw.compute_for == 'sales_person':
                    if (order.user_id and order.user_id in sales_person_list) and order.partner_id.is_affiliated:
                        name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                        invoice_commission_data = {'name' : name,
                                                   'user_id' : order.user_id.id,
                                                   'partner_id' : order.partner_id.id,
                                                   'commission_id' : commission_brw.id,
                                                   'type_name' : commission_brw.name,
                                                   'comm_type' : commission_brw.comm_type,
                                                   'partner_type' : 'Affiliated Partner',
                                                   'commission_amount' : affiliated_commission_amount,
                                                   'order_id' : order.id,
                                                   'date':datetime.datetime.today()}
                    elif (order.user_id and order.user_id in sales_person_list) and not order.partner_id.is_affiliated:
                        name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                        invoice_commission_data = {'name' : name,
                                                   'user_id' : order.user_id.id,
                                                   'partner_id' : order.partner_id.id,
                                                   'commission_id' : commission_brw.id,
                                                   'type_name' : commission_brw.name,
                                                   'comm_type' : commission_brw.comm_type,
                                                   'partner_type' : 'Non-Affiliated Partner',
                                                   'commission_amount' : non_affiliated_commission_amount,
                                                   'order_id' : order.id,
                                                   'date':datetime.datetime.today()}
                    if invoice_commission_data:
                        invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
                else:
                    sales_team = order.sale_commission_id.sales_team.filtered(lambda x: x == order.team_id)

                    if sales_team.team_manager and sales_team.manager_percentage:
                        if order.partner_id.is_affiliated:
                            name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                            invoice_commission_data = {'name' : name,
                                                       'user_id' : sales_team.team_manager.id,
                                                       'team_id' : sales_team.id,
                                                       'partner_id' : order.partner_id.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'partner_type' : 'Affiliated Partner',
                                                       'commission_amount' : affiliated_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}

                        else:
                            name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                            invoice_commission_data = {'name' : name,
                                                       'user_id' : sales_team.team_manager.id,
                                                       'team_id' : sales_team.id,
                                                       'partner_id' : order.partner_id.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'partner_type' : 'Non-Affiliated Partner',
                                                       'commission_amount' : non_affiliated_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                            if invoice_commission_data:
                                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))

                    if sales_team.user_id and sales_team.percentage:
                        if order.partner_id.is_affiliated:
                            name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                            invoice_commission_data = {'name' : name,
                                                       'user_id' : sales_team.user_id.id,
                                                       'team_id' : sales_team.id,
                                                       'partner_id' : order.partner_id.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'partner_type' : 'Affiliated Partner',
                                                       'commission_amount' : affiliated_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        else:
                            name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                            invoice_commission_data = {'name' : name,
                                                       'user_id' : sales_team.user_id.id,
                                                       'team_id' : sales_team.id,
                                                       'partner_id' : order.partner_id.id,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id' : line.product_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'partner_type' : 'Non-Affiliated Partner',
                                                       'commission_amount' : non_affiliated_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}

                        if invoice_commission_data:
                            invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))

                    if sales_team.normal_user_ids and sales_team.members_percentage:
                        if order.partner_id.is_affiliated:
                            for users in sales_team.normal_user_ids:
                                name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                                invoice_commission_data = {'name' : name,
                                                           'user_id' : users.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'product_id' : line.product_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'partner_type' : 'Affiliated Partner',
                                                           'commission_amount' : affiliated_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                                if invoice_commission_data:
                                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))

                        else:
                            for users in sales_team.normal_user_ids:
                                name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                                invoice_commission_data = {'name' : name,
                                                           'user_id' : users.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'product_id' : line.product_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'partner_type' : 'Non-Affiliated Partner',
                                                           'commission_amount' : non_affiliated_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                                if invoice_commission_data:
                                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
            else:
                for agents in self.agents_ids:
                    if order.partner_id.is_affiliated:
                        name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                        invoice_commission_data = {'name' : name,
                                                   'user_id' : order.user_id.id,
                                                   'agents' : agents.id,
                                                   'partner_id' : order.partner_id.id,
                                                   'commission_id' : commission_brw.id,
                                                   'type_name' : commission_brw.name,
                                                   'comm_type' : commission_brw.comm_type,
                                                   'partner_type' : 'Affiliated Partner',
                                                   'commission_amount' : affiliated_commission_amount,
                                                   'order_id' : order.id,
                                                   'date':datetime.datetime.today()}
                    else:
                        name = 'Partner commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                        invoice_commission_data = {'name' : name,
                                                   'user_id' : order.user_id.id,
                                                   'agents' : agents.id,
                                                   'partner_id' : order.partner_id.id,
                                                   'commission_id' : commission_brw.id,
                                                   'type_name' : commission_brw.name,
                                                   'comm_type' : commission_brw.comm_type,
                                                   'partner_type' : 'Non-Affiliated Partner',
                                                   'commission_amount' : non_affiliated_commission_amount,
                                                   'order_id' : order.id,
                                                   'date':datetime.datetime.today()}
                    if invoice_commission_data:
                        invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids

    # ==============================================================================================================================
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
                                           ('based_on', '=', 'product_categories'),])
            if exclusive_categ_exception_id:
                return exclusive_categ_exception_id
        return []

    #============================================================================================================================  
    def get_categ_commission(self, commission_brw, order):
        exception_obj = self.env['sale.commission.exception']
        invoice_commission_obj = self.env['sale.commission.lines']
        invoice_commission_ids = []
        for line in order.order_line:
            if not line.product_id:
                continue
            invoice_commission_data = {}
            exception_ids = []
            amount = line.price_subtotal

            exception_ids = self.get_exceptions(line, commission_brw)
            for exception in exception_ids:
                product_id = False
                categ_id = False
                name = ''

                if commission_brw.compute_free == 'percentage':
                    product_commission_amount = amount * (commission_brw.standard_commission / 100)
                else:
                    product_commission_amount = commission_brw.sale_commission

                if exception.based_on == "product_categories":
                    categ_id = exception.categ_id
                    if commission_brw.compute_free == 'percentage': 
                        name = 'Commission Exception for Product Category ' + tools.ustr(categ_id.name) + '" of ' + tools.ustr(commission_brw.standard_commission) + '%'
                    else:
                        product_commission_amount = commission_brw.sale_commission
                        name = 'Commission Exception for Product Category ' + tools.ustr(categ_id.name) + '" of Fix ' + tools.ustr(commission_brw.sale_commission)
                else:
                    product_id = exception.product_id
                    if commission_brw.compute_free == 'percentage': 
                        name = 'Commission Exception for Product ' + tools.ustr(exception.product_id.name) + '" of ' + tools.ustr(commission_brw.standard_commission) + '%'
                    else:
                        product_commission_amount = commission_brw.sale_commission
                        name = 'Commission Exception for Product ' + tools.ustr(exception.product_id.name) + '" of Fix ' + tools.ustr(commission_brw.sale_commission)

                if commission_brw.compute_for in ('sales_person', 'sales_team'):
                    print("You are in Sales Person")
                    if commission_brw.compute_for == 'sales_person':
                        if exception.based_on == "product_categories":
                            invoice_commission_data = {'name': name,
                                                       'commission_id' : commission_brw.id,
                                                       'categ_id': categ_id.id,
                                                       'user_id' : order.user_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : product_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        else:
                            invoice_commission_data = {'name': name,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id': product_id.id,
                                                       'user_id' : order.user_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : product_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
                    else:
                        sales_team = order.sale_commission_id.sales_team.filtered(lambda x: x == order.team_id)
                        if sales_team.team_manager and sales_team.manager_percentage:
                            manager_commission_amount= amount * (sales_team.manager_percentage / 100)
                            if exception.based_on == "product_categories":
                                name = 'Commission Exception for Product Category' + tools.ustr(categ_id.name) + '" of ' + tools.ustr(sales_team.manager_percentage) + '%' + ' For Manager'
                                invoice_commission_data = {'name': name,
                                                           'user_id' : sales_team.team_manager.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'categ_id': categ_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'commission_amount' : manager_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                            else:
                                name = 'Commission Exception for Product' + tools.ustr(exception.product_id.name) + '" of ' + tools.ustr(sales_team.manager_percentage) + '%' + ' For Manager'
                                invoice_commission_data = {'name': name,
                                                           'user_id' : sales_team.team_manager.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'product_id': product_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'commission_amount' : manager_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                            invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))

                        if sales_team.user_id and sales_team.percentage:
                            team_manager_commission_amount= amount * (sales_team.percentage / 100)
                            if exception.based_on == "product_categories":
                                name = 'Commission Exception for Product Category' + tools.ustr(categ_id.name) + '" of ' + tools.ustr(sales_team.percentage) + '%' + ' For Team Leader'
                                invoice_commission_data = {'name': name,
                                                           'user_id' : sales_team.user_id.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'categ_id': categ_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'commission_amount' : team_manager_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                            else:
                                name = 'Commission Exception for Product' + tools.ustr(exception.product_id.name) + '" of ' + tools.ustr(sales_team.percentage) + '%' + 'For Team Leader'
                                invoice_commission_data = {'name': name,
                                                           'user_id' : sales_team.user_id.id,
                                                           'team_id' : sales_team.id,
                                                           'partner_id' : order.partner_id.id,
                                                           'commission_id' : commission_brw.id,
                                                           'product_id': product_id.id,
                                                           'type_name' : commission_brw.name,
                                                           'comm_type' : commission_brw.comm_type,
                                                           'commission_amount' : team_manager_commission_amount,
                                                           'order_id' : order.id,
                                                           'date':datetime.datetime.today()}
                            invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))

                        if sales_team.normal_user_ids and sales_team.members_percentage:
                            for users in sales_team.normal_user_ids:
                                members_percentage_commission_amount= amount * (sales_team.members_percentage / 100)
                                if exception.based_on == "product_categories":
                                    name = 'Commission Exception for Product Category' + tools.ustr(categ_id.name) + '" of ' + tools.ustr(sales_team.members_percentage) + '%' + ' For Member'
                                    invoice_commission_data = {'name': name,
                                                               'user_id' : users.id,
                                                               'team_id' : sales_team.id,
                                                               'partner_id' : order.partner_id.id,
                                                               'commission_id' : commission_brw.id,
                                                               'categ_id': categ_id.id,
                                                               'type_name' : commission_brw.name,
                                                               'comm_type' : commission_brw.comm_type,
                                                               'commission_amount' : members_percentage_commission_amount,
                                                               'order_id' : order.id,
                                                               'date':datetime.datetime.today()}
                                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
                                else:
                                    name = 'Commission Exception for Product' + tools.ustr(exception.product_id.name) + '" of ' + tools.ustr(sales_team.members_percentage) + '%' + ' For Member'
                                    invoice_commission_data = {'name': name,
                                                               'user_id' : users.id,
                                                               'team_id' : sales_team.id,
                                                               'partner_id' : order.partner_id.id,
                                                               'commission_id' : commission_brw.id,
                                                               'product_id': product_id.id,
                                                               'type_name' : commission_brw.name,
                                                               'comm_type' : commission_brw.comm_type,
                                                               'commission_amount' : members_percentage_commission_amount,
                                                               'order_id' : order.id,
                                                               'date':datetime.datetime.today()}
                                    invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
                else:
                    for agents in self.agents_ids:
                        if exception.based_on == "product_categories":
                            invoice_commission_data = {'name': name,
                                                       'commission_id' : commission_brw.id,
                                                       'categ_id': categ_id.id,
                                                       'agents' : agents.id,
                                                       'user_id' : order.user_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : product_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        else:
                            invoice_commission_data = {'name': name,
                                                       'commission_id' : commission_brw.id,
                                                       'product_id': product_id.id,
                                                       'agents' : agents.id,
                                                       'user_id' : order.user_id.id,
                                                       'type_name' : commission_brw.name,
                                                       'comm_type' : commission_brw.comm_type,
                                                       'commission_amount' : product_commission_amount,
                                                       'order_id' : order.id,
                                                       'date':datetime.datetime.today()}
                        invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
    # ==============================================================================================================================

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == 'sale_order':
            self.get_sales_commission()
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            if so.commission_ids:
                so.commission_ids.sudo().unlink()
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'sol_id' : self.id})
        return res

