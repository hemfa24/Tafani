# Copyright (C) Softhealer Technologies.
from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_product_suggestion = fields.Boolean(
        "Enable Product Suggestion", default=False)
    
    enable_refund = fields.Boolean(
        "Enable Refund",default=True)
    enable_info = fields.Boolean(
        "Enable Info",default=True)
    enable_note = fields.Boolean(
        "Enable Note",default=True)
    enable_change_uom = fields.Boolean(
        "Enable Change UOM",default=True)
    enable_quick_order = fields.Boolean(
        "Enable Quick Order",default=True)
    enable_show_order = fields.Boolean(
        "Enable Show Order",default=True)
    
    enable_auto_pro_uom = fields.Boolean(
        "Enable Open Auto Product UOM Popup",default=True)
    
    enable_variant_popup = fields.Boolean(
        "Enable Open Variant Popup",default=True)
    

class PosOrder(models.Model):
    _inherit = "pos.order"

    def refund(self):
        refund_orders = self.env['pos.order']
        for order in self:
            current_session = order.session_id
            # if not current_session:
            #     raise UserError(_('To return product(s), you need to open a session in the POS %s', order.session_id.config_id.display_name))
            refund_order = order.copy(
                order._prepare_refund_values(current_session)
            )
            for line in order.lines:
                PosOrderLineLot = self.env['pos.pack.operation.lot']
                for pack_lot in line.pack_lot_ids:
                    PosOrderLineLot += pack_lot.copy()
                line.copy(line._prepare_refund_data(refund_order, PosOrderLineLot))
            refund_orders |= refund_order

        return {
            'name': _('Return Products'),
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': refund_orders.ids[0],
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }