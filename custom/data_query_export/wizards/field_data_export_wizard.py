import base64
import io
import xlwt
import logging
from datetime import datetime
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _write_in_export_sheet(worksheet, data):
    row = 0
    col = 0
    mer_row = row + 1
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour dark_purple;'
                               'font: color white, bold True;'
                               'alignment: horizontal center, vertical center;')
    for key_rec in list(data[0].keys()):
        worksheet.write_merge(row, mer_row, col, col, key_rec, header_style)
        col += 1
    row = 2
    for data_dic in data:
        col = 0
        for val in data_dic.values():
            worksheet.write(row, col, format(val))
            col += 1
        row += 1
    return True


def get_table_structure():
    table = """
                <table border="1" class="o_list_view table-bordered o_list_view_ungrouped">
                  <thead>
                {thead}
                  </thead>
                  <tbody>
                {tbody}
                  </tbody>
                </table>
            """
    thead = """
                <tr style="text-align: center;font-weight:bold ">
                {th}
                </tr>
            """
    th = """<th style='border: 1px solid #C0C0C0;position: sticky;top: 0;background: #ddd;padding: 3px;'>{}</th>\n"""
    td = """<td style='padding: 5px;'>{}</td>\n"""
    tr = """<tr>{}</tr>\n"""
    return table, thead, th, tr, td


class FieldDataExportWizard(models.TransientModel):
    _name = 'field.data.export.wizard'
    _rec_name = 'name'

    name = fields.Char(string='Name', default="Query")
    query_str = fields.Text(string="Query Input", required=1)
    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File', size=64)
    show_file = fields.Boolean(default=False)
    report_preview = fields.Html('Report Preview')

    @api.onchange('query_str')
    def onchange_query_str(self):
        self.write({'report_preview': '', 'show_file': False})

    def action_export(self):
        time_format = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        filename = 'Export File-{}.xls'.format(time_format)
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Export')
        data = self.generate_data_all()
        _write_in_export_sheet(worksheet, data)
        file_data = io.BytesIO()
        workbook.save(file_data)
        self.show_file = True
        self.excel_file = base64.b64encode(file_data.getvalue())
        self.file_name = filename
        return True

    def action_show(self):
        data = self.generate_data_all()
        column_header = [key_rec for key_rec in list(data[0].keys())]
        table, thead, th, tr, td = get_table_structure()
        head = thead.format(th="".join(map(th.format, column_header)))
        body = ''
        for data_dic in data:
            tbl_row = "<tr>"
            for val in data_dic.values():
                tbl_row += "<td>{}</td>".format(val)
            body += tbl_row + "</tr>"
        view_result = table.format(thead=head, tbody=body)
        self.write({'report_preview': view_result})
        return True

    def generate_data_all(self):
        sql = self.query_str
        try:
            self._cr.execute(sql)
        except Exception as msg:
            raise UserError(_("Query is not correct: \n %s", msg))
        results = self.env.cr.dictfetchall()
        return results

    def action_reload(self):
        return {
            'name': 'Query',
            'view_mode': 'form',
            'res_model': 'field.data.export.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
