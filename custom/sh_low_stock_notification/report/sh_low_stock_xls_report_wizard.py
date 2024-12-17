# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models, _
from odoo.exceptions import ValidationError, UserError

import xlwt
import base64
from io import BytesIO


class ShLowStockExcelExtended(models.Model):
    _name = "sh.low.stock.detail.excel.extended"
    _description = 'Excel Extended'

    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64)

    def download_report(self):

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=sh.low.stock.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (self.id, self.file_name),
            'target': 'new',
        }


class ShLowStockDetailsReportWizard(models.TransientModel):
    _name = "sh.low.stock.details.report.wizard"
    _description = 'Low Stock details report wizard model'

    def action_print_pdf_low_stock(self):
        datas = self.read()[0]
        return self.env.ref('sh_low_stock_notification.report_print_sh_low_stock_action').report_action([], data=datas)

    def print_low_stock_xls_report(self):
        if self.env.company.low_stock_notification:
            workbook = xlwt.Workbook()
            heading_format = xlwt.easyxf(
                'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center,vertical center;borders:top thick;borders:bottom thick;')
            bold = xlwt.easyxf(
                'font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz center,vertical center;')
            Center = xlwt.easyxf(
                'align: horiz center,vertical center;')
            self.env['product.low.stock.email'].notify_data()
            data = {}
            data = dict(data or {})

            if self.env.company.product_quantity_check == 'global':
                Name = 'Global'
            elif self.env.company.product_quantity_check == 'individual':
                Name = 'Individual'
            elif self.env.company.product_quantity_check == 'order_point':
                Name = 'Reorder Rules (Order Points)'

            Title = 'Low Stock' + \
                ' ( ' + Name + ' ) ' + 'Specified.'
            worksheet = workbook.add_sheet(
                Title, cell_overwrite_ok=True)
            worksheet.write_merge(
                0, 1, 0, 8, Title, heading_format)

            Products = self.env['product.low.stock.notify'].search([])
            if Products:
                worksheet.col(0).width = int(10 * 260)
                worksheet.col(1).width = int(35 * 260)
                worksheet.col(2).width = int(25 * 260)
                worksheet.col(3).width = int(25 * 260)
                worksheet.col(4).width = int(25 * 260)
                worksheet.col(5).width = int(25 * 260)

                worksheet.write_merge(5, 6, 0, 0, "Sr", bold)
                worksheet.write_merge(5, 6, 1, 1, "Product Name", bold)
                worksheet.write_merge(5, 6, 2, 2, "Default Code", bold)
                if self.env.company.sh_chouse_qty_type == 'on_hand':
                    worksheet.write_merge(5, 6, 3, 3, "On Hand Qty", bold)
                else:
                    worksheet.write_merge(5, 6, 3, 3, "Forcasted Qty", bold)

                worksheet.write_merge(5, 6, 4, 4, "Remaining Qty", bold)

                if self.env.company.product_quantity_check != 'global':
                    worksheet.write_merge(5, 6, 5, 5, "Minimum Qty", bold)

                count = 0

                journal_lines = []

                for lines in Products:
                    count += 1
                    product = {
                        'count': count,
                        'name': lines.name,
                        'def_code': lines.def_code or '',
                        'prod_qty': lines.prod_qty or '',
                        'remaining_qty': lines.remaining_qty or '',
                    }

                    if self.env.company.product_quantity_check != 'global':
                        product['min_qty'] = lines.min_qty

                    journal_lines.append(product)

                row = 7

                for rec in journal_lines:
                    if rec.get('count'):
                        worksheet.write_merge(
                            row, row, 0, 0, rec.get('count'), Center)
                        worksheet.write(row, 1, str(rec.get('name')) or '')
                        worksheet.write(row, 2, str(rec.get('def_code')) or '')
                        worksheet.write(row, 3, str(rec.get('prod_qty')) or '')
                        worksheet.write(row, 4, str(
                            rec.get('remaining_qty')) or '')
                        if self.env.company.product_quantity_check != 'global':
                            worksheet.write(row, 5, str(
                                rec.get('min_qty')) or '')

                    row += 1

                filename = (
                    'Low Stock Notification Detail Xls Report' + '.xls')
                fp = BytesIO()
                workbook.save(fp)
                export_id = self.env['sh.low.stock.detail.excel.extended'].sudo().create({
                    'excel_file': base64.encodebytes(fp.getvalue()),
                    'file_name': filename,
                })

                return {
                    'type': 'ir.actions.act_url',
                    'url': 'web/content/?model=sh.low.stock.detail.excel.extended&field=excel_file&download=true&id=%s&filename=%s' % (export_id.id, export_id.file_name),
                    'target': 'new',
                }
            else:
                raise ValidationError(_("There is no record to Display !!!"))
        else:
            raise UserError(_("Please Enable Low Stock Notification !!!"))
