from odoo.exceptions import UserError, ValidationError
from odoo import api, exceptions, fields, models, _
import io
import xlrd
import base64
from odoo.tools import pycompat
from odoo.exceptions import Warning


class NiImportProductGeneric(models.TransientModel):
    _name = 'product.generic.import.wizard'

    ni_file_type = fields.Selection([('xls', 'XLS File'),('csv', 'CSV File')], string='File Type',default='xls')
    ni_file_data = fields.Binary(string="File")
    ni_varient = fields.Selection([('none', 'None'),('create', 'Create'), ('update', 'Update')], string='Varient',default="none")
    ni_search_product = fields.Selection([('default_code', 'Internal Ref'), ('name', 'Name'), ('barcode', 'Barcode')],string='Search By Product',default='default_code')

    @api.onchange('ni_varient')
    def onchange_varient(self):
        if self.ni_varient != 'none':
            self.ni_search_product = 'name'

    def action_import_generic_product(self):
        product_template_obj = self.env['product.template']
        prod_att_obj = self.env['product.attribute']
        prod_att_value_obj = self.env['product.attribute.value']
        prod_tmpl_att_line_obj = self.env['product.template.attribute.line']
        product_category_obj = self.env['product.category']
        tax_obj = self.env['account.tax']
        product_uom_obj = self.env['uom.uom']
        if not self.ni_file_type:
            raise ValidationError(_('File type is not defined'))

        if self.ni_file_type == 'csv':
            csv_reader_data = pycompat.csv_reader(io.BytesIO(base64.decodestring(self.ni_file_data)), quotechar=",", delimiter=",")
            csv_reader_data = iter(csv_reader_data)
            next(csv_reader_data)
            ni_file_datas = csv_reader_data
        elif self.ni_file_type == 'xls':
            file_datas = base64.decodestring(self.ni_file_data)
            workbook = xlrd.open_workbook(file_contents=file_datas)
            sheet = workbook.sheet_by_index(0)
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
            del data[0][0:14]
            attribute_header = data[0]
            data.pop(0)
            ni_file_datas = data
        if ni_file_datas:
            for i in range(len(ni_file_datas)):
                keys = ['name', 'default_code', 'barcode', 'categ_id', 'type', 'uom_id', 'uom_po_id', 'list_price','standard_price', 'weight', 'volume', 'description_sale', 'taxes_id','supplier_taxes_id']
                field = map(str, ni_file_datas[i])
                product_values = dict(zip(keys, field))
                product_attribute_values = dict(zip(attribute_header, field))
                if product_values:
                    categ_id = product_category_obj.search([('name', '=', product_values.get('categ_id'))])
                    if not categ_id:
                        raise Warning('Category %s not found'%(product_values.get('categ_id')))
                    product_type = 'product'
                    if product_values.get('type') == 'Consumable':
                        product_type = 'consu'
                    elif product_values.get('type') == 'Service':
                        product_type = 'service'
                    uom_id = product_uom_obj.search([('name', '=', product_values.get('uom_id'))])
                    if not uom_id:
                        raise Warning('UOM %s not found'%(product_values.get('uom_id')))
                    uom_po_id = product_uom_obj.search([('name', '=', product_values.get('uom_po_id'))])
                    tax_ids = False
                    supplier_tax_ids = False
                    if product_values.get('taxes_id') != '':
                        tax_ids = tax_obj.search([('name','in',product_values.get('taxes_id').split(',')),('type_tax_use','=','sale')])

                    if product_values.get('supplier_taxes_id') != '':
                            supplier_tax_ids = tax_obj.search([('name','in',product_values.get('supplier_taxes_id').split(',')),('type_tax_use','=','purchase')],limit=1)
                    if tax_ids:
                        product_values.update({'taxes_id': [(6,0,tax_ids.ids)]})
                    else:
                        del product_values['taxes_id']

                    if supplier_tax_ids:
                        product_values.update({'supplier_taxes_id': [(6,0,supplier_tax_ids.ids)]})
                    else:
                        del product_values['supplier_taxes_id']

                    barcode = product_values.get('barcode')
                    if product_values.get('barcode'):
                        barcode = product_values.get('barcode').split('.')[0]
                    product_values.update({'type': product_type,
                                           'categ_id':categ_id.id,
                                           'uom_id':uom_id.id,
                                           'uom_po_id': uom_po_id.id if uom_po_id else uom_id.id,
                                           'list_price': float(product_values.get('list_price')),
                                           'standard_price': float(product_values.get('standard_price')),
                                           'weight': float(product_values.get('weight')),
                                           'volume': float(product_values.get('volume')),
                                           'barcode': barcode,
                                           })
                    if self.ni_search_product == 'default_code':
                        domain = [('default_code', '=', product_values.get('default_code'))]
                    elif self.ni_search_product == 'name':
                        domain = [('name', '=', product_values.get('name'))]
                    else:
                        domain = [('barcode','=',barcode)]

                    product_tmpl_id = product_template_obj.search(domain,limit=1)
                    if product_tmpl_id:
                        product_tmpl_id.write(product_values)
                    else:
                        product_tmpl_id = product_template_obj.create(product_values)
                    if attribute_header and self.ni_varient != 'none':
                        for attribute in attribute_header:
                            attribute_values = product_attribute_values.get(attribute)
                            attribute_id = prod_att_obj.search([('name', '=', attribute)],limit=1)
                            if not attribute_id:
                                raise Warning('Attribute %s not found' % (attribute))
                            prod_tmpl_att_line_id = prod_tmpl_att_line_obj.search([('product_tmpl_id', '=', product_tmpl_id.id), ('attribute_id', '=', attribute_id.id)])
                            if attribute_values and attribute_id:
                                attribute_value_id_list = []
                                for attribute_value in attribute_values.split(','):
                                    attribute_value_id = prod_att_value_obj.search([('name', '=', attribute_value)], limit=1)
                                    if not attribute_value_id:
                                        attribute_value_id = prod_att_value_obj.create({'name': attribute_value, 'attribute_id': attribute_id.id})
                                    attribute_value_id_list.append(attribute_value_id.id)

                                vals = {'value_ids': [(6, 0, attribute_value_id_list)], 'attribute_id': attribute_id.id}
                                if prod_tmpl_att_line_id:
                                    prod_tmpl_att_line_id.write(vals)
                                else:
                                    vals.update({'product_tmpl_id': product_tmpl_id.id})
                                    prod_tmpl_att_line_obj.create(vals)
                            else:
                                prod_tmpl_att_line_id.unlink()
