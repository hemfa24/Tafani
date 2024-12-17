# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime, format_date, groupby
from odoo.exceptions import UserError


class stockLocation(models.Model):
    _inherit = 'stock.location'

    is_intermediary_location = fields.Boolean()


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def _compute_picking_count(self):
        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', 'in', ['assigned','draft'])],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }
        for field in domains:
            data = self.env['stock.picking']._read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_request_id = fields.Many2one(
        'custom.warehouse.stock.request',
        string="Warehouse Stock Request",
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        
        res = super(StockPicking,self)._action_done()

        for rec in self:
            rec.request_work_validate()
        return res
        
    def action_confirm(self):
        for rec in self:
            if rec.stock_request_id and rec.stock_request_id.employee_id and rec.stock_request_id.stock_request_type == 'employee_request':
                
                if  rec.location_id.warehouse_id and rec.location_id.usage == 'internal' and rec.location_id.is_intermediary_location == False and rec.env.user.employee_id.id not in rec.stock_request_id.location_id.warehouse_id.employee_ids.ids:
                    raise UserError(_('Sorry Employee not have access to location '+rec.stock_request_id.location_id.complete_name))
                
                if  rec.location_dest_id.warehouse_id and rec.location_dest_id.usage == 'internal' and rec.location_dest_id.is_intermediary_location == False and rec.env.user.employee_id.id not in rec.location_dest_id.warehouse_id.employee_ids.ids:
                    raise UserError(_('Sorry Employee not have access to location '+rec.stock_request_id.location_dest_id.complete_name))
                
        res = super(StockPicking,self).action_confirm()

        return
        

    @api.model
    def create(self,vals):
        
        res = super(StockPicking, self).create(vals)
          
        for rec in res:
            stock_request_id = self.env['custom.warehouse.stock.request'].search([('name','=',rec.origin)])
            if stock_request_id and stock_request_id.stock_request_type == 'employee_request':
                if rec.location_id.usage == 'internal':
                    for emp in rec.location_id.warehouse_id.employee_ids:
                        if emp.user_id:

                            self.env['mail.activity'].create({
                            'display_name': 'text',
                            'summary': 'text',
                            'date_deadline': rec.scheduled_date,
                            'user_id': emp.user_id.id,
                            'res_id': rec.id,
                            'res_model_id': self.env['ir.model'].search([('model','=','stock.picking')],limit=1).id,
                            'activity_type_id': 4
                            })
                if rec.location_dest_id.usage == 'internal':
                    for emp in rec.location_dest_id.warehouse_id.employee_ids:
                        if emp.user_id:

                            self.env['mail.activity'].create({
                            'display_name': 'text',
                            'summary': 'text',
                            'date_deadline': rec.scheduled_date,
                            'user_id': emp.user_id.id,
                            'res_id': rec.id,
                            'res_model_id': self.env['ir.model'].search([('model','=','stock.picking')],limit=1).id,
                            'activity_type_id': 4
                            })

        return res

    @api.onchange('picking_type_id', 'partner_id')
    def _onchange_picking_type(self):
        ctx = self._context.copy()
        if not ctx.get('is_warehouse_stock_request'):
            return super(StockPicking, self)._onchange_picking_type()
        # if self.picking_type_id and self.state == 'draft' and not ctx.get('is_warehouse_stock_request'):
        #     self = self.with_company(self.company_id)
        #     if self.picking_type_id.default_location_src_id:
        #         location_id = self.picking_type_id.default_location_src_id.id
        #     elif self.partner_id:
        #         location_id = self.partner_id.property_stock_supplier.id
        #     else:
        #         customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

        #     if self.picking_type_id.default_location_dest_id:
        #         location_dest_id = self.picking_type_id.default_location_dest_id.id
        #     elif self.partner_id:
        #         location_dest_id = self.partner_id.property_stock_customer.id
        #     else:
        #         location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

        #     self.location_id = location_id
        #     self.location_dest_id = location_dest_id
        #     (self.move_lines | self.move_ids_without_package).update({
        #         "picking_type_id": self.picking_type_id,
        #         "company_id": self.company_id,
        #     })

        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in ('no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}


    

    def request_work_backorder(self):
        for rec in self:
            intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 

            if rec.stock_request_id.picking_type_id.code=='internal' and rec.stock_request_id.is_stock_request_type_stock and rec.location_id.id != intermediary_location:
                intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 
                stock_picking_obj = self.env['stock.picking']
                if rec.location_id.warehouse_id.employee_ids:
                    if self.env.user.employee_id.id not in rec.location_id.warehouse_id.employee_ids.ids:
                        raise UserError(_("You're not authorized to approved this order" ))
                line_vals =[]
                for line in self.move_ids_without_package:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity_done,
                        'product_uom': line.product_uom.id,
                        'description_picking': line.description_picking,
                        'name': line.description_picking,
                        'company_id': line.company_id.id,
                        # 'picking_type_id': rec.picking_type_id.id,
                        'picking_type_id': rec.stock_request_id.sec_picking_type_id.id,
                        'location_id':intermediary_location ,
                        'location_dest_id': rec.stock_request_id.location_dest_id.id,
                                }))

                vals = {
                        'partner_id': rec.partner_id.id,
                        # 'picking_type_id': rec.picking_type_id.id,
                        'picking_type_id': rec.stock_request_id.sec_picking_type_id.id,
                        'location_id': intermediary_location,
                        'location_dest_id': rec.stock_request_id.location_dest_id.id,
                        'scheduled_date': rec.scheduled_date,
                        'stock_request_id': rec.stock_request_id.id,
                        'move_ids_without_package': line_vals
                }
                picking_id = stock_picking_obj.with_context({
                'is_warehouse_stock_request':True
                }).create(vals)#.action_confirm()
                # picking_id.action_confirm()
            # else:
            #     return super(StockPicking, self).button_validate()

    def request_work_validate(self):
        for rec in self:
            intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 

            if rec.stock_request_id.picking_type_id.code=='internal' and rec.stock_request_id.is_stock_request_type_stock and rec.location_id.id != intermediary_location:
                intermediary_location = self.env.ref('hemfa_warehouse_stock_request.stock_location_intermediary').id 
                stock_picking_obj = self.env['stock.picking']
                if rec.location_id.warehouse_id.employee_ids:
                    if self.env.user.employee_id.id not in rec.location_id.warehouse_id.employee_ids.ids:
                        raise UserError(_("You're not authorized to approved this order" ))
                line_vals =[]
                for line in self.move_ids_without_package:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'description_picking': line.description_picking,
                        'name': line.description_picking,
                        'company_id': line.company_id.id,
                        # 'picking_type_id': rec.picking_type_id.id,
                        'picking_type_id': rec.stock_request_id.sec_picking_type_id.id,
                        'location_id':intermediary_location ,
                        'location_dest_id': rec.stock_request_id.location_dest_id.id,
                                }))

                vals = {
                        'partner_id': rec.partner_id.id,
                         'origin':rec.origin,
                        # 'picking_type_id': rec.picking_type_id.id,
                        'picking_type_id': rec.stock_request_id.sec_picking_type_id.id,
                        'location_id': intermediary_location,
                        'location_dest_id': rec.stock_request_id.location_dest_id.id,
                        'scheduled_date': rec.scheduled_date,
                        'stock_request_id': rec.stock_request_id.id,
                        'move_ids_without_package': line_vals
                }
                picking_id = stock_picking_obj.with_context({
                'is_warehouse_stock_request':True
                }).create(vals)#.action_confirm()
                # picking_id.action_confirm()
            # else:
            #     return super(StockPicking, self).button_validate()

class stockMove(models.Model):
    _inherit = 'stock.move'

    warehouse_stock_request_line_id = fields.Many2one('custom.warehouse.stock.request.line')
    @api.model
    def create(self, vals):
        res = super(stockMove, self).create(vals)
        
        return res












class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    _description = 'Backorder Confirmation'

    # def process(self):
    #     pickings_to_do = self.env['stock.picking']
    #     pickings_not_to_do = self.env['stock.picking']
    #     for line in self.backorder_confirmation_line_ids:
    #         if line.to_backorder is True:
    #             pickings_to_do |= line.picking_id
    #         else:
    #             pickings_not_to_do |= line.picking_id

    #     for pick_id in pickings_not_to_do:
    #         moves_to_log = {}
    #         for move in pick_id.move_lines:
    #             if float_compare(move.product_uom_qty,
    #                              move.quantity_done,
    #                              precision_rounding=move.product_uom.rounding) > 0:
    #                 moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
    #         pick_id._log_less_quantities_than_expected(moves_to_log)

    #     pickings_to_validate = self.env.context.get('button_validate_picking_ids')
    #     if pickings_to_validate:
    #         pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True)
    #         if pickings_not_to_do:
    #             pickings_to_validate = pickings_to_validate.with_context(picking_ids_not_to_backorder=pickings_not_to_do.ids)
    #         # pickings_to_validate.request_work_backorder()
    #         return pickings_to_validate.button_validate()
    #     return True

    # def process_cancel_backorder(self):
    #     pickings_to_validate = self.env.context.get('button_validate_picking_ids')
    #     if pickings_to_validate:
    #         pickings_to_validate_requests = self.env['stock.picking'].browse(pickings_to_validate)
            
    #         # pickings_to_validate_requests.request_work_backorder()
    #         return self.env['stock.picking']\
    #             .browse(pickings_to_validate)\
    #             .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids)\
    #             .button_validate()
    #     return True



class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'




    # def process(self):
    #     pickings_to_do = self.env['stock.picking']
    #     pickings_not_to_do = self.env['stock.picking']
    #     for line in self.immediate_transfer_line_ids:
    #         if line.to_immediate is True:
    #             pickings_to_do |= line.picking_id
    #         else:
    #             pickings_not_to_do |= line.picking_id

    #     for picking in pickings_to_do:
    #         # If still in draft => confirm and assign
    #         if picking.state == 'draft':
    #             picking.action_confirm()
    #             if picking.state != 'assigned':
    #                 picking.action_assign()
    #                 if picking.state != 'assigned':
    #                     raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
    #         picking.move_ids._set_quantities_to_reservation()

    #     pickings_to_validate = self.env.context.get('button_validate_picking_ids')
    #     if pickings_to_validate:
    #         pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
    #         pickings_to_validate = pickings_to_validate - pickings_not_to_do

    #         #override it so when create run clreate another picking
    #         # pickings_to_validate.with_context(skip_immediate=True).request_work_validate()
    #         return pickings_to_validate.with_context(skip_immediate=True).button_validate()
    #     return True






