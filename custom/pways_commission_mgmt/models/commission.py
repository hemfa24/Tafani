from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError, AccessError

class CreateCommisionInvoice(models.Model):
    _name = 'create.invoice.commission'
    _description = 'create invoice commission'

    group_by = fields.Boolean('Group By',default=True)
    date = fields.Date('Invoice Date',)

    def invoice_create(self):
        sale_invoice_ids = self.env['sale.commission.lines'].browse(self._context.get('active_ids'))
        
        if any(line.invoiced for line in sale_invoice_ids):
            raise ValidationError('Invoiced lines cannot be invoiced again.')

        commission_discount_account = self.env.user.company_id.commission_discount_account
        if not commission_discount_account:
            raise ValidationError('You have not configured commission account in sale configuration')
        
        journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        if not journal:
            raise ValidationError(_('Please define purchase type journal in acccountig for the company %s (%s).', self.env.company_id.name, self.env.company_id.id))
      
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

            fil_sales = sale_invoice_ids.filtered(lambda x: x.commission_id.compute_for in ('sales_person', 'sales_team'))

            if any(line.user_id != fil_sales[0].user_id for line in fil_sales):
                raise ValidationError('Please create bill for same salesperson only')

            for record in fil_sales:
                sales_group_dict.setdefault(record.user_id, []).append(record)

            for dict_record in sales_group_dict:
                partner = self.env['res.partner'].search([('id','=', dict_record.partner_id.id)], limit=1)
                for inv_record in sales_group_dict.get(dict_record):
                    sale_line_list.append((0, 0, {
                        'name': inv_record.name,
                        'account_id': commission_discount_account.id,
                        'quantity':1,
                        'price_unit': inv_record.commission_amount,
                    }))
                inv_id = self.env['account.move'].create({
                        'move_type':'in_invoice',
                        'partner_id': partner.id,
                        'journal_id': journal.id,
                        'invoice_date': self.date if self.date else datetime.datetime.today().date(),
                        'invoice_line_ids': sale_line_list,
                        'commission': True
                    })

            for dict_record in agent_group_dict:
                partner = self.env['res.partner'].search([('id','=', dict_record.id)], limit=1)
                for inv_record in agent_group_dict.get(dict_record):
                    agent_line_list.append((0, 0, {
                        'name': inv_record.name,
                        'account_id': commission_discount_account.id,
                        'quantity':1,
                        'price_unit': inv_record.commission_amount,
                    }))
                inv_id = self.env['account.move'].create({
                        'move_type':'in_invoice',
                        'partner_id': partner.id,
                        'journal_id': journal.id,
                        'invoice_date': self.date if self.date else datetime.datetime.today().date(),
                        'invoice_line_ids': agent_line_list,
                        'commission': True
                    })
                    
        else:
            for commission_record in sale_invoice_ids:
                inv_id = self.env['account.move'].create({
                        'move_type':'in_invoice',
                        'partner_id':commission_record.user_id.partner_id.id,
                        'journal_id': journal.id,
                        'invoice_date':self.date if self.date else datetime.datetime.today().date()
                })
                inv_line_id = self.env['account.move.line'].create({
                        'name':commission_record.name,
                        'account_id':commission_discount_account.id,
                        'quantity':1,
                        'price_unit':commission_record.commission_amount,
                        'move_id':inv_id.id
                })
        sale_invoice_ids.write({'invoiced': True})

class SaleCommission(models.Model):
    _name = 'sale.commission'
    _description = 'Sale commission'
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Commission Name', required=True)
    user_ids = fields.Many2many('res.users', 'commision_rel_user', 'commision_id', 'user_id' , string='Sales Person',help="Select sales person associated with this type of commission",required=False)
    exception_ids = fields.One2many('sale.commission.exception', 'commission_id')
    affiliated_partner_commission = fields.Float(string="Affiliated Percentage")
    nonaffiliated_partner_commission = fields.Float(string="Non-Affiliated Percentage")
    agents = fields.Many2many('res.partner',string="Agents", context={'default_agent': True})
    percentage = fields.Float(string="Percentage")
    team_manager = fields.Many2one('res.partner',string="Managers")
    comm_type = fields.Selection([('product','Product'),('categ','Product Category'),('partner','Partner'),('normal','Standard')],string="Commission Type",default="normal")
    sales_team = fields.Many2many('crm.team',string="Sales Team")
    compute_free = fields.Selection([('fix','Fix'),('percentage','Percentage')],string="Commission Value",required=True, default='fix')
    compute_for = fields.Selection([('sales_person','Sales Person'),('sales_team','Sales Team'),('agents','Agents')],string="Commission For", default='sales_person')
    standard_commission = fields.Float(string="Percentage %")
    sale_commission = fields.Float(string="Fix")
    compute_on = fields.Selection([("gross_amount","Gross Amount: "),("net_amount","Net Amount")], string="Compute On", default="gross_amount") 

    @api.constrains('compute_for')
    def _check_commpute_type(self):
        for rec in self:
            if rec.compute_for:
                if rec.compute_for == 'sales_person':
                    compute_for_type = self.env['sale.commission'].search([('compute_for', '=', 'sales_person')])
                    for x in compute_for_type:
                        if len(compute_for_type) > 1:
                            raise ValidationError(_("You Can't Create Sale Person Again"))
                if rec.compute_for == 'sales_team':
                    compute_for_type = self.env['sale.commission'].search([('compute_for', '=', 'sales_team')])
                    for x in compute_for_type:
                        if len(compute_for_type) > 1:
                            raise ValidationError(_("You Can't Create Sales Team Again"))
                if rec.compute_for == 'agents':
                    compute_for_type = self.env['sale.commission'].search([('compute_for', '=', 'agents')])
                    for x in compute_for_type:
                        if len(compute_for_type) > 1:
                            raise ValidationError(_("You Can't Create Agent Again"))

    @api.onchange("compute_for")
    def clear_values(self):
        self.sale_commission = False
        self.user_ids = False
        self.agents = False

    @api.onchange("compute_free")
    def clear_compute_free_value(self):
        self.standard_commission = False
        self.sale_commission = False

    @api.onchange("comm_type")
    def clear_comm_value(self):
        self.affiliated_partner_commission = False
        self.nonaffiliated_partner_commission = False

    @api.constrains('user_ids')
    def _check_uniqueness(self):
        for obj in self:
            ex_ids = self.search([('user_ids', 'in', [x.id for x in obj.user_ids])])
            if len(ex_ids) > 1:
                return False
        return True

    def _check_partners(self):
        obj = self.browse(cr, uid, ids[0], context=context)
        aff_partner = [x.id for x in obj.affiliated_partner_ids]
        nonaff_partner = [x.id for x in obj.nonaffiliated_partner_ids]
        common_partner = [x for x in aff_partner if x in nonaff_partner]
        if common_partner:
            return False
        return True

class SaleCommissionlines(models.Model):
    _name = 'sale.commission.lines'
    _description = 'Sale Commission lines'
    _inherit = ['mail.thread']
    _order = "id DESC"
    _rec_name = 'user_id'

    name = fields.Char(string="Description", size=512)
    type_name = fields.Char(string="Commission Name")
    comm_type = fields.Selection([('product','Product'),('categ','Product Category'),('partner','Partner'),('normal','Standard')],string="Commission Type",default="normal")
    user_id = fields.Many2one('res.users', string='Sales Person', help="sales person associated with this type of commission", required=True)
    commission_amount = fields.Float(string="Commission Amount")
    invoice_id = fields.Many2one('account.move', string='Invoice Reference', help="Affected Invoice")
    order_id = fields.Many2one('sale.order', string='Order Reference', help="Affected Sale Order")
    commission_id = fields.Many2one('sale.commission', string='Sale Commission', help="Related Commission",)
    product_id = fields.Many2one('product.product', string='Product',help="product",)
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_type = fields.Selection([('Affiliated Partner', 'Affiliated Partner'), ('Non-Affiliated Partner', 'Non-Affiliated Partner')], string='Partner Type')
    categ_id = fields.Many2one('product.category', string='Product Category')
    date = fields.Date('Date')
    invoiced = fields.Boolean(string='Invoiced', readonly=True, default=False)
    agents = fields.Many2one('res.partner',string="Agent")
    team_id = fields.Many2one('crm.team',string="Sales Team")
    state = fields.Selection([('draft', 'Draft'), ('invoice', 'Invoice'), ('done','Done'),('cancel', 'Cancel')], string='State', default="draft")

class SaleCommissionTeam(models.Model):
    _inherit = 'crm.team'

    team_manager = fields.Many2one('res.users',string="Manager")
    member_ids = fields.Many2many('res.users',string="Members")
    percentage = fields.Float(string="Team Leader Percentage")
    manager_percentage = fields.Float(string="Manager Percentage")
    members_percentage = fields.Float(string="Member Percentage")
    normal_user_ids = fields.Many2many('res.users',string="Normal Members")

class SaleCommissionException(models.Model):
    _name = 'sale.commission.exception'
    _rec_name = 'based_on'
    _description = 'Sale Commission Exception'

    based_on = fields.Selection([('products', 'Products'),('product_categories', 'Product Categories')], store=True, string="Based On", help="commission exception based on", compute='_compute_for_based_on')
    commission_id = fields.Many2one('sale.commission', help="Related Commission")
    product_id = fields.Many2one('product.product', string='Product',help="Exception based on product",)
    categ_id = fields.Many2one('product.category', string='Product Category',help="Exception based on product category")
    comm_type = fields.Selection(string="Commission Type",related='commission_id.comm_type')

    @api.depends('comm_type')
    def _compute_for_based_on(self):
        for record in self:
            if not record.based_on:
                if record.comm_type:
                    if record.comm_type == 'product':
                        record.based_on = 'products'
                    elif record.comm_type == 'categ':
                        record.based_on = 'product_categories'
                    else: 
                        record.based_on = False