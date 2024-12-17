# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, models, _
from odoo.exceptions import UserError


class LowStockReport(models.AbstractModel):
    _name = 'report.sh_low_stock_notification.sh_low_stock_report_template'
    _description = "Low Stock Report"

    @api.model
    def _get_report_values(self, docids, data=None):

        if self.env.company.low_stock_notification:
            report_data = {}
            count = 0

            self.env['product.low.stock.email'].notify_data()

            Products = self.env['product.low.stock.notify'].search([])

            if Products:
                if self.env.company.product_quantity_check == 'global':
                    Name = 'Global'
                elif self.env.company.product_quantity_check == 'individual':
                    Name = 'Individual'
                elif self.env.company.product_quantity_check == 'order_point':
                    Name = 'Reorder Rules (Order Points)'

                for line in Products:
                    data_dic = {}
                    count += 1
                    data_dic = {
                        'count': count,
                        'name': line.name,
                        'def_code': line.def_code,
                        'prod_qty': line.prod_qty,
                        'min_qty': line.min_qty,
                        'remaining_qty': line.remaining_qty,

                    }
                    report_data.update({line.id: data_dic})
                data = {
                    'sh_doc': report_data,
                    'company_id': self.env.company,
                    'name': Name,
                }
                return data
            else:
                raise UserError(_("There is no record to Display !!!"))
        else:
            raise UserError(_("Please Enable Low Stock Notification !!!"))
