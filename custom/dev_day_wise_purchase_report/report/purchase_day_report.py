# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models


class PurchaseDaysReport(models.AbstractModel):
    _name = 'report.dev_day_wise_purchase_report.purchase_report_template'

    def get_day_number(self, data, product_id, day):

        purchase_line = self.env['purchase.order.line'].search([('order_id.date_order', '>=', data.start_date),
                                                        ('order_id.date_order', '<=', data.end_date),
                                                        ('product_id', '=', product_id)
                                                        ])
        number = 0
        for line in purchase_line:
            days = line.order_id.date_order.strftime("%A")
            if days == day:
                number += 1
        return int(number)

    def get_data(self, data):
        domain = ('state','in',['done','purchase'])
        if data.print_in_draft:
            domain = ('state','in',['draft','done','purchase'])
        purchase_line = self.env['purchase.order.line'].search([('order_id.date_order', '>=', data.start_date),('order_id.date_order', '<=', data.end_date),('order_id.company_id', 'in', data.company_ids.ids),domain])
        final_list = []
        product_data = []
        for line in purchase_line:
            if line.product_id.id not in product_data:
                product_data.append(line.product_id.id)
                final_list.append({'product_name': line.product_id.name,
                                   'monday': self.get_day_number(data, line.product_id.id, 'Monday'),
                                   'tuesday': self.get_day_number(data, line.product_id.id, 'Tuesday'),
                                   'wednesday': self.get_day_number(data, line.product_id.id, 'Wednesday'),
                                   'thursday': self.get_day_number(data, line.product_id.id, 'Thursday'),
                                   'friday': self.get_day_number(data, line.product_id.id, 'Friday'),
                                   'saturday': self.get_day_number(data, line.product_id.id, 'Saturday'),
                                   'sunday': self.get_day_number(data, line.product_id.id, 'Sunday'),

                                   })

        return final_list

    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.days.wizard'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'purchase.days.wizard',
            'docs': docs,
            'proforma': True,
            'get_data': self.get_data(docs),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
