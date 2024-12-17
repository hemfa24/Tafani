# Copyright © 2018 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from typing import List

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import _lang_get


class PrintProductLabel(models.TransientModel):
    _name = "print.product.dynamic.label"  
    #_inherit = "print.product.label"

    _description = 'Wizard to print Product Labels'

    @api.model
    def _complete_label_fields(self, label_ids: List[int]) -> List[int]:
        """Set additional fields for product labels. Method to override."""
        return label_ids

    @api.model
    def _get_product_label_ids(self):
        res = []
        # flake8: noqa: E501
        if self._context.get('active_model') == 'product.template':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['print.product.dynamic.label.line'].create({
                    'product_id': product.product_variant_id.id,
                })
                res.append(label.id)
        elif self._context.get('active_model') == 'product.product':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['print.product.dynamic.label.line'].create({
                    'product_id': product.id,
                })
                res.append(label.id)
        res = self._complete_label_fields(res)
        return res

    name = fields.Char(default='Print Product Labels')
    message = fields.Char(readonly=True)
    output = fields.Selection(
        selection=[('pdf', 'PDF')],
        string='Print to',
        default='pdf',
    )
    label_ids = fields.One2many(
        comodel_name='print.product.dynamic.label.line',
        inverse_name='wizard_id',
        string='Labels for Products',
       # default=_get_product_label_ids,
    )
    report_id = fields.Many2one(
        comodel_name='ir.actions.report',
        string='Label',
        domain=[('model', '=', 'print.product.dynamic.label.line')],
    )
    is_template_report = fields.Boolean(compute='_compute_is_template_report')
    qty_per_product = fields.Integer(
        string='Label quantity per product',
        default=1,
    )
    # Options
    humanreadable = fields.Boolean(
        string='Human readable barcode',
        help='Print digital code of barcode.',
        default=False,
    )
    border_width = fields.Integer(
        string='Border',
        help='Border width for labels (in pixels). Set "0" for no border.'
    )
    lang = fields.Selection(
        selection=_lang_get,
        string='Language',
        help="The language that will be used to translate label names.",
    )

    @api.depends('report_id')
    def _compute_is_template_report(self):
        for wizard in self:
            # flake8: noqa: E501
            wizard.is_template_report = self.report_id == self.env.ref('garazd_dynamic_product_label.action_report_product_label_from_template_dynamic')

    def get_labels_to_print(self):
        self.ensure_one()
        labels = self.label_ids.filtered('selected')
        if not labels:
            raise UserError(
                _('Nothing to print, set the quantity of labels in the table.'))
        return labels

    def _get_report_action_params(self):
        """Return two params for a report action: record "ids" and "data"."""
        self.ensure_one()
        return self.get_labels_to_print().ids, None

    def action_print(self):
        """Print labels."""
        self.ensure_one()
        mode = self._context.get('print_mode', 'pdf')
        if not self.report_id:
            raise UserError(_('Please select a label type.'))
        report = self.report_id.with_context(discard_logo_check=True, lang=self.lang)
        report.sudo().write({'report_type': f'qweb-{mode}'})
        return report.report_action(*self._get_report_action_params())

    def action_set_qty(self):
        """Set a specific number of labels for all lines."""
        self.ensure_one()
        self.label_ids.write({'qty': self.qty_per_product})

    barcode = fields.Char(default='Print Product Labels')
    @api.depends('report_id')
    @api.onchange('barcode')
    def onchange_barcode_set_product(self):
        for rec in self:
            if rec.barcode:
               # product_id = self.env['product.product'].search([('barcode', '=', rec.barcode)])
                search_product_code = self.env["product.template.barcode"].sudo().search(
                    [('name', '=', rec.barcode),
                     ('available_item', '=', True)
                     ], limit=1)

                if search_product_code:
                    lines = rec.label_ids.filtered(lambda
                                                            l: l.product_id.id == search_product_code.product_id.id and l.barcode == search_product_code.name)
                    if lines:
                        for line in lines:
                            line.qty += 1
                    else:
                        set_price_stand = 0.0
                        obj_price_stand = self.env['product.pricelist.item'].sudo().search([
                            ('product_id', '=', search_product_code.product_id.id),
                            ('multi_barcode', '=', search_product_code.name),

                        ], limit=1)

                        print('\n\n\n-------- obj_price_stand ------', obj_price_stand)
                        price_lst =False
                        if obj_price_stand:
                            set_price_stand = obj_price_stand.fixed_price
                            price_lst =obj_price_stand.pricelist_id.id
                        else:
                            set_price_stand = search_product_code.price
                            price_lst =False
                        line_val = {
                            'product_id': search_product_code.product_id.id,
                            'qty': 1,
                            'wizard_id': self.id,
                            'selected': True,
                            'barcode': search_product_code.name,
                            'price' : set_price_stand,
                            'pricelist_id' : price_lst,

                        }

                        rec.label_ids = [(0, 0, line_val)]
                else:
                    pass
                    # raise UserError(
                    #     _("Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (
                    #         rec.barcode))
            rec.barcode = False

    # def action_restore_initial_qty(self):
    #     """Restore the initial number of labels for all lines."""
    #     self.ensure_one()
    #     for label in self.label_ids:
    #         if label.qty_initial:
    #             label.update({'qty': label.qty_initial})
