# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
class stockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    employee_ids = fields.Many2many('hr.employee',string="Employee Aceess")

class CustomWarehouseStockRequest(models.Model):
    _name = 'custom.warehouse.stock.request'
    _description = "Warehouse Stock Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
        readonly= True,
        copy=False
    )

    stock_request_type = fields.Selection([
        ('purchase_request', 'Purchase Request'),
        ('employee_request', 'Employee Request'),
        # ('stock','Stock')
        ],
        # default='stock_request',
        string="Request type",
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Contact",
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    employee_id = fields.Many2one(
        'hr.employee',copy=False)

    

    request_date = fields.Datetime(
        string="Requested Date",
        default=lambda self: fields.Datetime.now(),
        required= True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string="Operation Type",
        required= True,
        readonly=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}
    )
    location_id = fields.Many2one(
        'stock.location',
        string="Source Location",
        required= True,
        readonly=True,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        string="Destination Location",
        required= True,
        readonly=True,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company', 
        store=True, 
        change_default=True,
        required= True,
        default=lambda self: self.env.company,
        readonly=True,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    created_user_id = fields.Many2one(
        'res.users',
        string="Created By",
        readonly=True,
        default=lambda self: self.env.user,
        copy=False
    )
    approve_user_id = fields.Many2one(
        'res.users',
        string="Approved By",
        readonly=True,
        copy=False
    )

    is_purchased = fields.Boolean(string='Is purchased', default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('done', 'Received'),
        ('cancel', 'Cancelled')],
        default='draft',
        string="Status",
        copy=False
    )
    warehouse_stock_request_line_ids = fields.One2many(
        'custom.warehouse.stock.request.line',
        'stock_request_id',
        string="Request Lines",
        readonly=True,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    note = fields.Text(
        string="Notes",
        readonly=True,
        copy=True,
        states={'draft': [('readonly', False)],'confirmed': [('readonly', False)]}
    )
    operation_type_code = fields.Selection(related="picking_type_id.code",readonly=1)
    barcode = fields.Char()
    sec_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string="Second Operation Type",
     )

    is_stock_request_type_stock = fields.Boolean()

    @api.onchange('location_id','location_dest_id','picking_type_id','stock_request_type')
    def onchange_set_is_stock_request_type_stock(self):
        for rec in self:
            rec.is_stock_request_type_stock = False
            if rec.location_id and rec.location_dest_id and rec.picking_type_id and rec.stock_request_type:
                if rec.picking_type_id.code == 'internal' and rec.location_id.usage == 'internal' and rec.location_dest_id.usage == 'internal' and rec.stock_request_type == 'employee_request':
                    rec.is_stock_request_type_stock = True
            else:
                rec.sec_picking_type_id = False



    @api.onchange('barcode')
    def onchange_barcode_set_product(self):
        for rec in self:
            if rec.barcode:
                product_id = self.env['product.product'].search([('barcode','=',rec.barcode)])
                if product_id:
                    lines = rec.warehouse_stock_request_line_ids.filtered(lambda l: l.product_id.id == product_id.id)
                    if lines:
                        for line in lines:
                            line.demand_qty += 1
                    else:
                        line_val = {
                                    # 'inventory_id': rec.id,
                                    'product_id': product_id.id,
                                    'description':product_id.display_name,
                                    'product_uom':product_id.uom_id.id,
                                    'demand_qty': 1,
                                    
                                }

                        rec.warehouse_stock_request_line_ids = [(0, 0, line_val)]
            rec.barcode = False

    @api.onchange('employee_id','stock_request_type')
    def onchange_employee_set_partner(self):
        for rec in self:
            if rec.employee_id and rec.stock_request_type == 'employee_request':
                rec.partner_id = rec.employee_id.user_id.partner_id.id
            else:
                rec.employee_id = rec.partner_id = False
    
    # @api.constrains('employee_id','stock_request_type','location_id','location_dest_id')
    # def check_employee_access(self):
    #     for rec in self:
    #         if rec.employee_id and rec.stock_request_type == 'employee_request':
                
    #             if  rec.location_id.warehouse_id and rec.employee_id.id not in rec.location_id.warehouse_id.employee_ids.ids:
    #                 raise UserError(_('Sorry Employee not have access to location '+rec.location_id.complete_name))
    #             if  rec.location_dest_id.warehouse_id and rec.employee_id.id not in rec.location_dest_id.warehouse_id.employee_ids.ids:
    #                 raise UserError(_('Sorry Employee not have access to location '+rec.location_dest_id.complete_name))
            

    def action_warehouse_stock_request_send(self):
        self.ensure_one()
        template = self.env.ref('hemfa_warehouse_stock_request.email_template_edi_warehouse_stock_request')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='custom.warehouse.stock.request',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout='mail.mail_notification_light',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('stock_request_type')
    def _get_default_picking_type(self):
        if self.stock_request_type == 'purchase_request':
            self.picking_type_id = self.env['stock.picking.type'].search([('name', '=', 'Receipts')], limit=1).id
            self.location_id = self.env['stock.location'].search([('complete_name', '=', 'Partners/Vendors')], limit=1).id
        elif self.stock_request_type == 'employee_request':
            self.picking_type_id = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')], limit=1).id
            self.location_id = self.picking_type_id.default_location_src_id.id
            self.location_dest_id = self.env['stock.location'].search([('complete_name', '=', 'Partners/Employees')],
                                                                 limit=1).id
            print("test")
        else:
            self.picking_type_id = False
            self.location_dest_id = False

    # @api.onchange('picking_type_id')
    # def onchange_picking_type_id(self):
    #     for rec in self:
    #         rec.location_dest_id = rec.picking_type_id.default_location_dest_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('custom.warehouse.stock.request')
        return super(CustomWarehouseStockRequest, self).create(vals_list)

    def show_transfers_picking(self):
        self.ensure_one()
        action = self.env.ref("stock.action_picking_tree_all")
        action = action.sudo().read()[0]
        action['domain'] = str([('stock_request_id', '=', self.id)])
        action['context'] = {'default_stock_request_id': self.id}
        return action

    def show_product_on_hand(self):
        self.ensure_one()
        action = self.env.ref("stock.dashboard_open_quants")
        action = action.sudo().read()[0]
        product_ids = []
        for line in self.warehouse_stock_request_line_ids:
            product_ids.append(line.product_id.id)
        action['domain'] = str([('product_id', 'in', product_ids)])
        action['context'] = {
            'search_default_on_hand':1,
            'search_default_productgroup':1, 
        }
        return action

    def custom_action_confirmed(self):
        self.ensure_one()
        self.state = 'confirmed'
        if self.stock_request_type == 'purchase_request' :
            users_ids = self.env['res.users'].search([]).filtered(lambda l: l.has_group('purchase.group_purchase_user'))
            for user in users_ids:
                self.env['mail.activity'].create({
                            'display_name': 'text',
                            'summary': 'text',
                            'date_deadline': self.request_date,
                            'user_id': user.id,
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].search([('model','=','custom.warehouse.stock.request')],limit=1).id,
                            'activity_type_id': 4
                            })

    def custom_action_approved(self):
        stock_picking_obj = self.env['stock.picking']
        line_vals = []

        if self.picking_type_id.code=='internal' and self.is_stock_request_type_stock:
            
            intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 
            i=0
            for line in self.warehouse_stock_request_line_ids:
                if line.demand_qty <= 0:
                    raise UserError(_('Demand QTY Must Be Greater than Zero for All Lines'))
                
                line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.demand_qty,
                    'product_uom': line.product_uom.id,
                    'description_picking': line.description+'-'+str(i),
                    'name': line.description,
                    'company_id': line.company_id.id,
                    'picking_type_id': line.stock_request_id.picking_type_id.id,
                    'location_id': line.stock_request_id.location_id.id,
                    'location_dest_id': intermediary_location,
                    'warehouse_stock_request_line_id':line.id,
                }))
                i = i+1
            if not line_vals:
                raise UserError(_('Request Line Is Empty , Please Fill it First'))
            
            vals = {
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': intermediary_location,
                'scheduled_date': self.request_date,
                'stock_request_id': self.id,
                'move_ids_without_package': line_vals,
                'origin':self.name,   
            }

            
            picking_id = stock_picking_obj.with_context({
                'is_warehouse_stock_request':True
            }).create(vals)
            # picking_id.action_confirm()
           
        else:        
        

            action = self.env.ref("stock.action_picking_tree_all").read()[0]
            self.ensure_one()
            context = {
                'default_partner_id': self.partner_id.id,
                'default_picking_type_id': self.picking_type_id.id,
                'default_location_id': self.location_id.id,
                'default_location_dest_id': self.location_dest_id.id,
                'default_scheduled_date': self.request_date,
                'default_stock_request_id': self.id,
                'is_warehouse_stock_request': True,
                'default_origin':self.name,
            }
            line_vals = []
            for line in self.warehouse_stock_request_line_ids:
                line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.demand_qty,
                    'product_uom': line.product_uom.id,
                    'description_picking': line.description,
                    'name': line.description,
                    'company_id': line.company_id.id,
                    'picking_type_id': line.stock_request_id.picking_type_id.id,
                    'location_id': line.stock_request_id.location_id.id,
                    'location_dest_id': line.stock_request_id.location_dest_id.id,
                }))
            if line_vals:
                context.update({
                    'default_move_ids_without_package': line_vals  ,
                    'is_stock_request':True,  
                })
            
            
            self.env['stock.picking'].with_context(context).create({})
            # action['context'] = context
        self.state = 'approved'

    def custom_action_done(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('stock_request_id', '=', rec.id)])
            if picking_ids:
                rec.approve_user_id = self.env.user.id

                if any(p.state not in ['done','cancel'] for p in picking_ids):
                    raise UserError(_('Still picking transfer related to this request is not done yet so please validate it first.'))
            rec.state = 'done'

    def custom_action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def custom_action_draft(self):
        for rec in self:
            rec.state = 'draft'





class CustomWarehouseStockRequestLine(models.Model):
    _name = 'custom.warehouse.stock.request.line'
    _description = "Warehouse Stock Request Line"

    stock_request_id = fields.Many2one(
        'custom.warehouse.stock.request',
        string="Warehouse Stock Request",
        copy=False,
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required= True
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string="UOM",
        required= True
    )
    demand_qty = fields.Float(
        string="Demand Qty",
        required= True
    )
    company_id = fields.Many2one(
        string='Company', 
        store=True, 
        readonly=True,
        related='stock_request_id.company_id', 
        change_default=True, 
        default=lambda self: self.env.company
    )

    request_date = fields.Datetime(related="stock_request_id.request_date",store=True)
   

    @api.onchange('product_id')
    def onchange_product(self):
        for rec in self:
            rec.description = rec.product_id.display_name
            rec.product_uom = rec.product_id.uom_id.id