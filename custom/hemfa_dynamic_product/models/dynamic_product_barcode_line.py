# -*- coding: utf-8 -*-

import time
import json
import io
import datetime
import tempfile
import binascii
import xlrd
import itertools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, exceptions, api, _
import logging
from operator import itemgetter

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class DynamicProductBarcodeLine(models.TransientModel):
    _name = "dynamic.product.barcode.line"
    _description = "Dynamic Product Barcode"

    file_to_upload = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='csv')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)

    def search_product(self,product_name):
        return self.env['product.product'].search([('name', 'ilike', product_name)],limit=1)

    def search_uom(self,unit_name):
        return self.env['uom.uom'].search([('name', 'ilike', unit_name)],limit=1)

    def search_pricelist(self,pricelist_name):
        return self.env['product.pricelist'].search([('name', 'ilike', pricelist_name)],limit=1)

    def action_import_lines(self):
        if self.import_option == 'csv':
            try:
                csv_data = base64.b64decode(self.file_to_upload)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Invalid file!"))

            lines_to_create = []
            for line in file_reader[1:]:
                product=self.search_product(line[0])
                uom = self.search_uom(line[2])
                pricelist = self.search_pricelist(line[3])
                available_item = True if line[5] in ['1.0','1','True','true'] else False
                negative_qty_price = True if line[6] in ['1.0','1','True','true'] else False
                if product:
                    new_line = {
                        'product_id': product.id,
                        'name': line[1],
                        'unit': uom.id,
                        'available_item':available_item,
                        'negative_qty_price': negative_qty_price
                    }
                    if pricelist:
                        new_line['price_lst'] = pricelist.id
                    else:
                        new_line['price']=float(line[4])
                    lines_to_create.append(new_line)
                
            self.env['product.template.barcode'].create(lines_to_create)
        else:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_to_upload))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_('Invalid File!!'))
            lines_to_create = []
            for index in range(1,sheet.nrows):
                line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(index)))
                product=self.search_product(line[0])
                uom = self.search_uom(line[2])
                pricelist = self.search_pricelist(line[3])
                available_item = True if line[5] in ['1.0','1','True','true'] else False
                negative_qty_price = True if line[6] in ['1.0','1','True','true'] else False
                if product:
                    new_line = {
                        'product_id': product.id,
                        'name': line[1],
                        'unit': uom.id,
                        'available_item':available_item,
                        'negative_qty_price': negative_qty_price
                    }
                    if pricelist:
                        new_line['price_lst'] = pricelist.id
                    else:
                        new_line['price']=float(line[4])
                    lines_to_create.append(new_line)
            self.env['product.template.barcode'].create(lines_to_create)