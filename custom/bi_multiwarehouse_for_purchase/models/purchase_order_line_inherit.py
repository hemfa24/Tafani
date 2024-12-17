# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)

        allow_purchase_warehouse = self.env.user.company_id.allow_purchase_warehouse
        result['is_warehouse'] = allow_purchase_warehouse

        return result

    is_warehouse = fields.Boolean(string="warehouse", related="company_id.allow_purchase_warehouse")

class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'


    warehouses_id = fields.Many2one('stock.warehouse', string="Warehouse")
    is_warehouse = fields.Boolean()

    @api.onchange('product_id')
    def set_required_warehouse(self):
        allow_purchase_warehouse = self.env['ir.config_parameter'].sudo().get_param(
            'bi_multiwarehouse_for_purchase.allow_purchase_warehouse')
        self.is_warehouse = allow_purchase_warehouse
        if self.product_id:
            self.warehouses_id = self.product_id.purchase_warehouse_id.id

    def create_stock_moves(self, picking):
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line.prepare_stock_moves(picking):
                values.append(val)
            line.move_dest_ids.created_purchase_line_id = False
        return self.env['stock.move'].create(values)

    def prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res

        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')

        move_dests = self.move_dest_ids
        if not move_dests:
            move_dests = self.move_ids.move_dest_ids.filtered(
                lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier')

        if not move_dests:
            qty_to_attach = 0
            qty_to_push = self.product_qty - qty
        else:
            move_dests_initial_demand = self.product_id.uom_id._compute_quantity(
                sum(move_dests.filtered(lambda m: m.state !=
                    'cancel' and not m.location_dest_id.usage == 'supplier').mapped('product_qty')),
                self.product_uom, rounding_method='HALF-UP')
            qty_to_attach = move_dests_initial_demand - qty
            qty_to_push = self.product_qty - move_dests_initial_demand

        if float_compare(qty_to_attach, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(
                qty_to_attach, self.product_id.uom_id)
            res.append(self.prepare_stock_move_vals(
                picking, price_unit, product_uom_qty, product_uom))
        if float_compare(qty_to_push, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(
                qty_to_push, self.product_id.uom_id)
            extra_move_vals = self.prepare_stock_move_vals(
                picking, price_unit, product_uom_qty, product_uom)
            extra_move_vals['move_dest_ids'] = False  # don't attach
            res.append(extra_move_vals)
        return res

    def prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        product = self.product_id.with_context(
            lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        description_picking = product._get_description(
            self.order_id.picking_type_id)
        if self.product_description_variants:
            description_picking += "\n" + self.product_description_variants
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.warehouses_id.lot_stock_id.id,
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.warehouses_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
        }
