# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductLowStockNotify(models.Model):
    _name = "product.low.stock.notify"
    _description = 'save data to display in email'

    name = fields.Char("Product")
    def_code = fields.Char("Default Code")
    prod_qty = fields.Float("Quantity")
    min_qty = fields.Float("Minimum Quantity")
    remaining_qty = fields.Float("Remaining Quantity")
    email_id = fields.Many2one("product.low.stock.email",)
    company_id = fields.Many2one('res.company', required=True,
                                 default=lambda self: self.env.company)

    sh_qty_type = fields.Selection(
        related='company_id.product_quantity_check', string='Select Quantity Type', store=True)


class ProductLowStockEmail(models.Model):
    _name = "product.low.stock.email"
    _description = 'sends email'

    name = fields.Char("Product Low Stock Email")
    notify_ids = fields.One2many(
        "product.low.stock.notify", "email_id", "Notify Id")
    company_id = fields.Many2one('res.company', required=True,
                                 default=lambda self: self.env.company)

    @api.model
    def notify_data(self):
        if self.env.company.low_stock_notification:
            notify = self.env['product.low.stock.notify'].search([])
            if notify:
                notify.unlink()

            if self.env.company.notify_user_id:
                if self.env.company.notify_user_id.email:

                    selected_companies = self.env['res.company'].browse(
                        self._context.get('allowed_company_ids'))

                    if self.env.company.product_quantity_check == 'global':
                        glb_min_qty = self.env.company.minimum_quantity

                        products = self.env['product.product'].sudo().search(
                            ['|', ('company_id', 'in', selected_companies.ids), ('company_id',  '=', False)])

                        line_list = []
                        if products:
                            for product in products:
                                quant = self.env['stock.quant'].sudo().search(
                                    [('product_id', '=', product.id), ('company_id', 'in', selected_companies.ids)])

                                qty = quant.mapped('quantity')

                                final_qty = sum([n for n in qty if n > 0])

                                available_qty = quant.mapped(
                                    'available_quantity')

                                final_available_qty = sum(
                                    [n for n in available_qty if n > 0])

                                quantity = 0.0
                                if self.env.company.sh_chouse_qty_type == 'on_hand':
                                    quantity = final_qty
                                else:
                                    quantity = final_available_qty

                                if quantity < glb_min_qty:
                                    vals_line = {'name': product.name_get(
                                    )[0][1], 'prod_qty': quantity, 'min_qty': glb_min_qty, 'remaining_qty':  glb_min_qty-quantity, 'email_id': 1}
                                    if product.default_code:
                                        vals_line.update(
                                            {'def_code': product.default_code})
                                    else:
                                        vals_line.update({'def_code': ''})
                                    line_list.append(vals_line)

                        lines = []
                        if len(line_list) > 0:
                            for line in range(len(line_list)):
                                if line_list[line] not in line_list[line + 1:]:
                                    lines.append((0, 0, line_list[line]))

                        user_email_search = self.env['product.low.stock.email'].search([
                        ])
                        if lines and user_email_search:
                            user_email_search.notify_ids = lines
                            user_email_search.company_id = self.env.company.id

                    elif self.env.company.product_quantity_check == 'individual':
                        products = self.env['product.product'].sudo().search(
                            ['|', ('company_id', 'in', selected_companies.ids), ('company_id',  '=', False)])

                        vals_list = []

                        if products:
                            for product in products:

                                quant = self.env['stock.quant'].sudo().search(
                                    [('product_id', '=', product.id), ('company_id', 'in', selected_companies.ids)])

                                qty = quant.mapped('quantity')

                                final_qty = sum([n for n in qty if n > 0])

                                available_qty = quant.mapped(
                                    'available_quantity')

                                final_available_qty = sum(
                                    [n for n in available_qty if n > 0])

                                quantity = 0.0
                                if self.env.company.sh_chouse_qty_type == 'on_hand':
                                    quantity = final_qty
                                else:
                                    quantity = final_available_qty

                                # if self.env.company.sh_chouse_qty_type == 'on_hand':
                                #     quantity += product.qty_available
                                # else:
                                #     quantity += product.virtual_available
                                # company_products = self.env['res.company.product'].sudo().search(
                                #     [('company_id', '=', self.env.company.id), ('product_id', '=', product.id)])

                                minimum_qty = 0.0
                                # if company_products:
                                #     for company_product in company_products:
                                minimum_qty = product.minimum_quantity
                                if quantity < product.minimum_quantity:
                                    vals_line = {'name': product.name_get(
                                    )[0][1], 'prod_qty': quantity, 'min_qty': minimum_qty, 'remaining_qty':  product.minimum_quantity-quantity, 'email_id': 1}
                                    if product.default_code:
                                        vals_line.update(
                                            {'def_code': product.default_code})
                                    else:
                                        vals_line.update(
                                            {'def_code': ''})
                                    vals_list.append(vals_line)
                        lines = []
                        if len(vals_list) > 0:
                            for line in range(len(vals_list)):
                                if vals_list[line] not in vals_list[line + 1:]:
                                    lines.append((0, 0, vals_list[line]))
                        user_email_search = self.env['product.low.stock.email'].search([
                        ])
                        if lines and user_email_search:
                            user_email_search.notify_ids = lines
                            user_email_search.company_id = self.env.company.id

                    elif self.env.company.product_quantity_check == 'order_point':
                        products = self.env['product.product'].sudo().search(
                            ['|', ('company_id', 'in', selected_companies.ids), ('company_id',  '=', False)])
                        vals_list = []
                        if products:
                            for product in products:
                                quant = self.env['stock.quant'].sudo().search(
                                    [('product_id', '=', product.id), ('company_id', 'in', selected_companies.ids)])

                                qty = quant.mapped('quantity')

                                final_qty = sum([n for n in qty if n > 0])

                                available_qty = quant.mapped(
                                    'available_quantity')

                                final_available_qty = sum(
                                    [n for n in available_qty if n > 0])

                                quantity = 0.0
                                if self.env.company.sh_chouse_qty_type == 'on_hand':
                                    quantity = final_qty
                                else:
                                    quantity = final_available_qty

                                order_points = self.env['stock.warehouse.orderpoint'].sudo().search(
                                    [('product_id', '=', product.id), ('company_id', 'in', selected_companies.ids)])

                                if order_points:
                                    for order_point in order_points:
                                        if quantity < order_point.product_min_qty:
                                            vals_line = {'name': product.name_get(
                                            )[0][1], 'prod_qty': quantity, 'min_qty': order_point.product_min_qty, 'remaining_qty':  order_point.product_min_qty-quantity, 'email_id': 1}
                                            if product.default_code:
                                                vals_line.update(
                                                    {'def_code': product.default_code})
                                            else:
                                                vals_line.update(
                                                    {'def_code': ''})
                                            vals_list.append(vals_line)
                        lines = []
                        if len(vals_list) > 0:
                            for line in range(len(vals_list)):
                                if vals_list[line] not in vals_list[line + 1:]:
                                    lines.append((0, 0, vals_list[line]))
                        user_email_search = self.env['product.low.stock.email'].search([
                        ])
                        if lines and user_email_search:
                            user_email_search.notify_ids = lines
                            user_email_search.company_id = self.env.company.id

        else:
            raise UserError(_("Please Enable Low Stock Notification !!!"))

    @api.model
    def notify_user_fun(self):
        if self.env.company.low_stock_notification:
            self.notify_data()
            template = self.env.ref(
                'sh_low_stock_notification.template_product_stock_low_notify_email')
            if template:
                template.send_mail(1, force_send=True)
        else:
            raise UserError(_("Please Enable Low Stock Notification !!!"))
