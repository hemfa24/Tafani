from odoo.exceptions import UserError, ValidationError
from odoo import api, exceptions, fields, models, _
import io
import xlrd
import base64
from odoo.tools import pycompat
from odoo.exceptions import Warning
import csv
import time

import threading
import logging

_logger = logging.getLogger(__name__)


class ResDivision(models.Model):
    _name = 'res.division'
    _rec_name = 'name'
    _description = 'New division'

    name = fields.Char(string='Division Name')


class NewModule(models.Model):
    _inherit = 'product.template'

    division_id = fields.Many2one(comodel_name="res.division", string="Division", required=False, )


class NiImportProductTemplate(models.TransientModel):
    _name = 'product.template.import.wizard'
    _description = "Import Product Template"

    ni_file_type = fields.Selection([('xls', 'XLS File'), ('csv', 'CSV File')], string='File Type', default='xls')
    ni_file_data = fields.Binary(string="File")
    ni_variant = fields.Selection([('none', 'None'), ('create_update', 'Create/Update')], string='Variant',
                                  default="none")
    ni_search_product = fields.Selection([('default_code', 'Internal Ref'), ('name', 'Name'), ('barcode', 'Barcode')],
                                         string='Search By Product', default='default_code')
    is_custom_script = fields.Boolean(string="Product Create / Update")
    re_import_script = fields.Boolean(string="Re-Import")

    def action_import_product_template(self):
        if self.is_custom_script:
            self.action_threading_call()
        else:
            self.import_product_template()

    def action_threading_call(self):
        if self.ni_file_data:
            threaded_calculation = threading.Thread(target=self.product_create_update_template, args=())
            threaded_calculation.start()
        else:
            raise UserError(_("File not Found...!!!"))

    def import_product_template(self):
        product_template_obj = self.env['product.template']
        product_var_create = []
        product_obj = self.env['product.product']
        prod_att_obj = self.env['product.attribute']
        prod_att_value_obj = self.env['product.attribute.value']
        prod_tmpl_att_line_obj = self.env['product.template.attribute.line'].with_context(from_import=True)
        prod_tmpl_att_value_obj = self.env['product.template.attribute.value']
        product_category_obj = self.env['product.category']
        product_brand_obj = self.env['pos.product.brand']
        product_model_obj = self.env['product.model']
        product_sex_obj = self.env['product.sex']
        product_college_obj = self.env['product.college']
        tax_obj = self.env['account.tax']
        product_uom_obj = self.env['uom.uom']
        division_id_obj = self.env['res.division']

        if not self.ni_file_data:
            raise ValidationError(_('File is not defined'))

        if self.ni_file_type == 'csv':
            csv_data = base64.b64decode(self.ni_file_data)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            data = []
            res = {}
            csv_reader = csv.reader(data_file, delimiter=',')
            data.extend(csv_reader)
        elif self.ni_file_type == 'xls':
            file_datas = base64.decodebytes(self.ni_file_data)
            workbook = xlrd.open_workbook(file_contents=file_datas, encoding_override="utf-8")
            sheet = workbook.sheet_by_index(0)
            data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(20000)]

            del data[0][0:22]
            attribute_header = data[0]
            data.pop(0)
            ni_file_datas = data

        if ni_file_datas:
            for i in range(len(ni_file_datas)):
                prod_temp_keys = ['name', 'default_code', 'barcode', 'categ_id', 'product_brand_id', 'type', 'uom_id',
                                  'uom_po_id', 'list_price', 'standard_price', 'weight', 'volume', 'description_sale',
                                  'taxes_id', 'supplier_taxes_id', 'division_id']
                prod_var_keys = ['default_code', 'barcode', 'model_id', 'sex_id', 'college_id', 'standard_price']

                field = map(str, ni_file_datas[i])

                product_values = dict(zip(prod_temp_keys, field))
                product_variant_values = dict(zip(prod_var_keys, field))
                product_attribute_values = dict(zip(attribute_header, field))
                if product_values:
                    categ_id = product_category_obj.search([('name', '=', product_values.get('categ_id'))])
                    if not categ_id:
                        # raise Warning('Category %s not found'%(product_values.get('categ_id')))
                        categ_id = product_category_obj.create({'name': product_values.get('categ_id')})

                    product_brand_id = product_brand_obj.search([('name', '=', product_values.get('product_brand_id'))])
                    if not product_brand_id:
                        # raise Warning('Brand %s not found'%(product_values.get('product_brand_id')))
                        product_brand_id = product_brand_obj.create({'name': product_values.get('product_brand_id')})

                    product_type = 'product'
                    if product_values.get('type') == 'Consumable':
                        product_type = 'consu'
                    elif product_values.get('type') == 'Service':
                        product_type = 'service'
                    print("\n\n\n product_values.get('uom_id'), ,", product_values.get('uom_id'))
                    uom_id = product_uom_obj.search([('name', '=', product_values.get('uom_id'))])
                    if not uom_id:
                        raise ValidationError(_('UOM %s not found' % (product_values.get('uom_id'))))
                    uom_po_id = product_uom_obj.search([('name', '=', product_values.get('uom_po_id'))])
                    tax_ids = False
                    supplier_tax_ids = False
                    division_id = division_id_obj.search(
                        [('name', '=', product_values.get('division_id'))])
                    if not division_id:
                        division_id = division_id_obj.create(
                            {'name': product_values.get('division_id')})
                    if product_values.get('taxes_id') != '':
                        tax_ids = tax_obj.search(
                            [('name', 'in', product_values.get('taxes_id').split(',')), ('type_tax_use', '=', 'sale')])

                    if product_values.get('supplier_taxes_id') != '':
                        supplier_tax_ids = tax_obj.search(
                            [('name', 'in', product_values.get('supplier_taxes_id').split(',')),
                             ('type_tax_use', '=', 'purchase')], limit=1)
                    if tax_ids:
                        product_values.update({'taxes_id': [(6, 0, tax_ids.ids)]})
                    else:
                        del product_values['taxes_id']

                    if supplier_tax_ids:
                        product_values.update({'supplier_taxes_id': [(6, 0, supplier_tax_ids.ids)]})
                    else:
                        del product_values['supplier_taxes_id']

                    barcode = product_values.get('barcode')
                    if product_values.get('barcode'):
                        barcode = product_values.get('barcode').split('.')[0]

                    check_pt_barcode = product_template_obj.search([('barcode', '=', barcode)], limit=1)
                    if check_pt_barcode:
                        barcode = False

                    product_values.update({'type': product_type,
                                           'categ_id': categ_id.id,
                                           'product_brand_id': product_brand_id.id,
                                           'uom_id': uom_id.id,
                                           'uom_po_id': uom_po_id.id if uom_po_id else uom_id.id,
                                           'list_price': float(product_values.get('list_price')),
                                           'standard_price': float(product_values.get('standard_price')),
                                           'weight': float(product_values.get('weight')),
                                           'volume': float(product_values.get('volume')),
                                           'barcode': barcode,
                                           'division_id': division_id.id,

                                           #    'available_in_pos': True,
                                           })
                    if self.ni_search_product == 'default_code':
                        domain = [('default_code', '=', product_values.get('default_code'))]
                    elif self.ni_search_product == 'name':
                        domain = [('name', '=', product_values.get('name'))]
                    else:
                        domain = [('barcode', '=', barcode)]

                    product_tmpl_id = product_template_obj.search(domain, limit=1)
                    if product_tmpl_id:
                        product_tmpl_id.write(product_values)
                    else:
                        product_tmpl_id = product_template_obj.create(product_values)
                    print("product_tmpl_id", product_tmpl_id)

                    if attribute_header and self.ni_variant != 'none':
                        attributes_value_ids = []
                        for attribute in attribute_header:
                            attribute_value = product_attribute_values.get(attribute)
                            attribute_id = prod_att_obj.search([('name', '=', attribute)], limit=1)
                            if attribute_id:
                                if attribute_id.create_variant != 'no_variant':
                                    raise Warning('Attribute : ( %s ) variant creation mode is not ( Never )' % (
                                        attribute_id.name))
                            else:
                                attribute_id = prod_att_obj.create({'name': attribute, 'create_variant': 'no_variant'})

                            prod_tmpl_att_line_id = prod_tmpl_att_line_obj.search(
                                [('product_tmpl_id', '=', product_tmpl_id.id), ('attribute_id', '=', attribute_id.id)])

                            if attribute_value and attribute_id and attribute_value != '':
                                attribute_value_id_list = []
                                attribute_value_id = prod_att_value_obj.search(
                                    [('name', '=', attribute_value), ('attribute_id', '=', attribute_id.id)], limit=1)
                                if not attribute_value_id:
                                    attribute_value_id = prod_att_value_obj.create(
                                        {'name': attribute_value, 'attribute_id': attribute_id.id})
                                attribute_value_id_list.append(attribute_value_id.id)
                                attributes_value_ids.append(attribute_value_id.id)

                                vals = {}
                                if not attribute_value_id in prod_tmpl_att_line_id.value_ids:
                                    vals = {'value_ids': [(4, attribute_value_id.id)], 'attribute_id': attribute_id.id}

                                if prod_tmpl_att_line_id:
                                    prod_tmpl_att_line_id.write(vals)
                                else:
                                    vals.update({'product_tmpl_id': product_tmpl_id.id})
                                    prod_tmpl_att_line_obj.create(vals)


                            else:
                                prod_tmpl_att_line_id.unlink()

                        if product_tmpl_id and product_variant_values:
                            # prod_att_value_ids = prod_att_value_obj.browse(attributes_value_ids)
                            # prod_tmpl_att_value_ids = prod_att_value_ids
                            prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search(
                                [('product_tmpl_id', '=', product_tmpl_id.id),
                                 ('product_attribute_value_id', 'in', attributes_value_ids)])
                            # product_id = product_obj.search([('product_tmpl_id', '=', product_tmpl_id.id), ('product_template_attribute_value_ids', '=', prod_tmpl_att_value_ids.ids)], limit=1)
                            if prod_tmpl_att_value_ids:
                                print("exits")
                            combination = prod_tmpl_att_value_ids._only_active()
                            is_combination_possible = product_tmpl_id._is_combination_possible_by_config(combination,
                                                                                                         ignore_no_variant=False)

                            if is_combination_possible:
                                v_default_code = product_variant_values.get('default_code').split('.')[0]
                                if not product_variant_values.get('default_code') or product_variant_values.get(
                                        'default_code') == ' ':
                                    v_default_code = product_tmpl_id.default_code

                                model_id = product_model_obj.search(
                                    [('name', '=', product_variant_values.get('model_id'))])
                                if not model_id:
                                    # raise Warning('Product Model %s not found'%(product_variant_values.get('model_id')))
                                    model_id = product_model_obj.create(
                                        {'name': product_variant_values.get('model_id')})

                                sex_id = product_sex_obj.search([('name', '=', product_variant_values.get('sex_id'))])
                                if not sex_id:
                                    # raise Warning('Product Sex %s not found'%(product_variant_values.get('sex_id')))
                                    sex_id = product_sex_obj.create({'name': product_variant_values.get('sex_id')})

                                college_id = product_college_obj.search(
                                    [('name', '=', product_variant_values.get('college_id'))])
                                if not college_id:
                                    # raise Warning('Product college %s not found'%(product_variant_values.get('college_id')))
                                    college_id = product_college_obj.create(
                                        {'name': product_variant_values.get('college_id')})

                                variant_barcode = product_variant_values.get('barcode')
                                if variant_barcode:
                                    variant_barcode = product_variant_values.get('barcode').split('.')[0]
                                else:
                                    variant_barcode = False

                                product_variant_values.update({
                                    'product_tmpl_id': product_tmpl_id.id,
                                    'default_code': v_default_code,
                                    'barcode': variant_barcode,
                                    'model_id': model_id.id,
                                    'sex_id': sex_id.id,
                                    'college_id': college_id.id,
                                    'product_brand_id': product_brand_id.id,
                                    'standard_price': float(product_variant_values.get('standard_price')),
                                    # 'available_in_pos': True,
                                    'product_template_attribute_value_ids': [(6, 0, combination.ids)],
                                    'active': product_tmpl_id.active,
                                })

                                if self.ni_search_product == 'barcode':
                                    odj = self.env['product.product'].search([('barcode', '=', variant_barcode)])
                                    if not odj:
                                        product_var_create.append(product_variant_values)
                                elif self.ni_search_product == 'default_code':
                                    odj = self.env['product.product'].search([('default_code', '=', v_default_code)])
                                    if not odj:
                                        product_var_create.append(product_variant_values)
                                else:
                                    product_var_create.append(product_variant_values)

            for varient in product_var_create:
                product_obj.create(varient)

    """
        New Code Updated on
        Product Template
    """

    def product_create_update_template(self):
        this = self
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))

            product_template_obj = self.env['product.template']
            product_obj = self.env['product.product']
            prod_att_obj = self.env['product.attribute']
            prod_att_value_obj = self.env['product.attribute.value']
            prod_tmpl_att_line_obj = self.env['product.template.attribute.line'].with_context(from_import=True)
            prod_tmpl_att_value_obj = self.env['product.template.attribute.value']
            product_category_obj = self.env['product.category']
            product_brand_obj = self.env['pos.product.brand']
            product_uom_obj = self.env['uom.uom']

            model_obj = self.env['product.model']
            sex_obj = self.env['product.sex']
            college_obj = self.env['product.college']
            division_obj = self.env['res.division']
            aggroup_obj = self.env['age.group']
            ptgroup_obj = self.env['product.type.group']
            collections_obj = self.env['product.collections']
            seasonality_obj = self.env['seasonality.seasonality']

            ni_file_datas = False

            if self.ni_file_type == 'xls':
                file_datas = base64.decodebytes(self.ni_file_data)
                workbook = xlrd.open_workbook(file_contents=file_datas, encoding_override="utf-8")
                sheet = workbook.sheet_by_index(0)
                data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]
                del data[0][0:22]
                attribute_header = data[0]
                data.pop(0)
                ni_file_datas = data
            else:
                raise ValidationError(_('Sorry But only Only xls file accepted..!!'))

            """
                Version Name Genarted base on File Formate
            """
            Attributes = []
            Color_id = prod_att_obj.search([('name', '=', 'Color')], limit=1)
            if not Color_id:
                Color_id = prod_att_obj.create(
                    {
                        'name': 'Color',
                        'display_type': 'color'
                    }
                )
            Attributes.append(Color_id)

            Size_id = prod_att_obj.search([('name', '=', 'Size')], limit=1)
            if not Size_id:
                Size_id = prod_att_obj.create({'name': 'Size'})
            Attributes.append(Size_id)

            limit = 1000
            count = 1
            T_count = 1
            for line in ni_file_datas:
                name = line[0]
                category = line[3]
                default_code = line[16]
                barcode = line[17]
                cost = line[21]
                brand = line[4]
                product_type = line[5]
                umo = line[6]
                po_umo = line[7]
                price = line[8] or 0.0
                weight = line[9] or 0.0
                volume = line[10] or 0.0
                sale_info = line[11] or 0.0

                division = line[15]
                V_model = line[18]
                V_Sex = line[19]
                V_College = line[20]
                V_Color = line[22]
                V_Size = line[23]

                Nex_text_cells = line[24]
                ModelNber = line[25]
                Collections = line[26]
                Seasonality = line[27]
                Material_composition = line[28]
                Product_type_group = line[29]
                Age_group = line[30]
                Available_in_pos = True if line[31] == 1 else False

                if barcode:
                    barcode = str(barcode).split('.')[0]

                categ_id = False
                brand_id = False
                umo_id = False
                po_umo_id = False
                V_model_id = False
                V_Sex_id = False
                V_College_id = False
                division_id = False
                age_group_id = False
                product_type_group_id = False
                collection_id = False
                seasonality_id = False
                if category:
                    categ_id = product_category_obj.search([
                        ('name', '=', category)
                    ], limit=1)
                    if not categ_id:
                        categ_id = product_category_obj.with_context({
                                'skip_log': True
                            }).create({'name': category})

                if brand:
                    brand_id = product_brand_obj.search([
                        ('name', '=', brand)
                    ])
                    if not brand_id:
                        brand_id = product_brand_obj.with_context({
                                'skip_log': True
                            }).create({'name': brand})
                if umo:
                    umo_id = product_uom_obj.search([('name', '=', umo)], limit=1)
                if po_umo:
                    po_umo_id = product_uom_obj.search([('name', '=', po_umo)], limit=1)

                if division:
                    division_id = division_obj.search([('name', '=', division)])
                    if not division_id:
                        division_id = division_obj.with_context({
                                'skip_log': True
                            }).create({'name': division})

                if V_model:
                    V_model_id = model_obj.search([
                        ('name', '=', V_model)
                    ], limit=1)
                    if not V_model_id:
                        V_model_id = model_obj.with_context({
                                'skip_log': True
                            }).create({'name': V_model})

                if V_Sex:
                    V_Sex_id = sex_obj.search([
                        ('name', '=', V_Sex)
                    ], limit=1)
                    if not V_Sex_id:
                        V_Sex_id = sex_obj.with_context({
                                'skip_log': True
                            }).create({'name': V_Sex})
                print ("V_College", V_College)
                if V_College:
                    V_College_id = college_obj.search([
                        ('name', '=', V_College)
                    ], limit=1)
                    if not V_College_id:
                        V_College_id = college_obj.with_context({
                                'skip_log': True
                            }).create({'name': V_College})

                if Age_group:
                    age_group_id = aggroup_obj.search([
                        ('name', '=', Age_group)
                    ], limit=1)
                    if not age_group_id:
                        age_group_id = aggroup_obj.with_context({
                                'skip_log': True
                            }).create({'name': Age_group})

                if Product_type_group:
                    product_type_group_id = ptgroup_obj.search([
                        ('name', '=', Product_type_group)
                    ], limit=1)
                    if not product_type_group_id:
                        product_type_group_id = ptgroup_obj.with_context({
                                'skip_log': True
                            }).create({'name': Product_type_group})

                if Seasonality:
                    seasonality_id = seasonality_obj.search([
                        ('name', '=', Seasonality)
                    ], limit=1)
                    if not seasonality_id:
                        seasonality_id = seasonality_obj.with_context({
                                'skip_log': True
                            }).create({'name': Seasonality})

                if Collections:
                    collection_id = collections_obj.search([
                        ('name', '=', Collections)
                    ], limit=1)
                    if not collection_id:
                        collection_id = collections_obj.with_context({
                                'skip_log': True
                            }).create({'name': Collections})

                vals = {
                    'name': name,
                    'default_code': default_code,
                    'import_unique_code': default_code,
                    'categ_id': categ_id.id if categ_id else False,
                    'detailed_type': 'product' if product_type == 'StorableProduct' else 'consu',
                    'weight': weight,
                    'volume': volume,
                    'standard_price': cost,
                    'list_price': price,
                    'division_id': division_id.id if division_id else False,
                    'description_sale': sale_info,
                    'product_brand_id': brand_id.id if brand_id else False,
                    'model_id': V_model_id.id if V_model_id else False,
                    'sex_id': V_Sex_id.id if V_Sex_id else False,
                    'college_id': V_College_id.id if V_College_id else False,
                }
                if umo_id:
                    vals.update({'uom_id': umo_id.id})
                if po_umo_id:
                    vals.update({'uom_po_id': po_umo_id.id})

                print("barcode - - ---- -Start -- -- - ", barcode, V_College_id)
                template_id = product_template_obj.search(
                    [('import_unique_code', '=', default_code), ('college_id', '=', V_College_id.id)], limit=1)
                prod_verinet = product_obj.search([('barcode', '=', barcode)])
                print("prod_verinet Found ", prod_verinet)
                if prod_verinet:
                    continue
                else:
                    if self.re_import_script:
                        if not template_id.product_variant_ids.filtered(
                                lambda x: x.barcode == barcode and x.seasonality_id.id == seasonality_id.id):
                            """
                                new	old	old	old	new	creat new product template

                                When New barncode come and with Season
                            """
                            print("522222")
                            new_template_id = product_template_obj.with_context({
                                'skip_log': True
                            }).create(vals)
                            # vals.update({

                            # })
                            # new_template_id.product_variant_ids[0].write(vals)
                            product_attribute_value = []
                            list_of_vals = []
                            for att in Attributes:
                                att_line_id = prod_tmpl_att_line_obj.search([
                                    ('product_tmpl_id', '=', new_template_id.id),
                                    ('attribute_id', '=', att.id)
                                ])
                                print ("('attribute_id', '=', att.id)", att, V_Size)
                                if att.name == 'Size' and V_Size:
                                    V_Size_id = False
                                    if isinstance(V_Size, float):
                                        V_Size = str(int(V_Size))
                                    V_Size_id = prod_att_value_obj.search([
                                        ('name', '=', V_Size),
                                        ('attribute_id', '=', att.id)
                                        ])
                                    if not V_Size_id:
                                        V_Size_id = prod_att_value_obj.with_context({
                                            'skip_log': True
                                        }).create({
                                            'name': V_Size,
                                            'attribute_id': att.id
                                        })
                                    if att_line_id:
                                        att_line_id.write({'value_ids': [(4, V_Size_id.id)]})
                                        self.env.cr.commit()
                                    else:
                                        list_of_vals.append({
                                            'value_ids': [(4, V_Size_id.id)],
                                            'product_tmpl_id': new_template_id.id,
                                            'attribute_id': att.id
                                        })
                                    if V_Size_id:
                                        product_attribute_value.append(V_Size_id.id)
                                if att.name == 'Color' and V_Color != 'unknowing':
                                    V_Color_id = prod_att_value_obj.search([
                                        ('name', '=', V_Color),
                                        ('attribute_id', '=', att.id)
                                    ])
                                    if not V_Color_id:
                                        V_Color_id = prod_att_value_obj.with_context({
                                                'skip_log': True
                                        }).create({
                                            'name': V_Color,
                                            'attribute_id': att.id
                                        })
                                    if att_line_id:
                                        att_line_id.write({'value_ids': [(4, V_Color_id.id)]})
                                        self.env.cr.commit()
                                    else:
                                        list_of_vals.append({
                                            'value_ids': [(4, V_Color_id.id)],
                                            'product_tmpl_id': new_template_id.id,
                                            'attribute_id': att.id
                                        })
                                    if V_Color_id:
                                        product_attribute_value.append(V_Color_id.id)
                            if list_of_vals:
                                prod_tmpl_att_line_obj.with_context({
                                    'skip_log': True
                                }).create(list_of_vals)
                                prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search([
                                    ('product_tmpl_id', '=', new_template_id.id),
                                    ('product_attribute_value_id', 'in', product_attribute_value)
                                ])
                                prod_verinet_ids = product_obj.search([
                                    ('product_template_attribute_value_ids', 'in', prod_tmpl_att_value_ids.ids)
                                ])
                                prod_verinet_ids.write({
                                    'standard_price': cost,
                                    'barcode': barcode,
                                    'nex_text_cells': Nex_text_cells,
                                    'model_no': ModelNber,
                                    'barcode': barcode,
                                    'default_code': default_code,
                                    'seasonality_id': seasonality_id.id if seasonality_id else False,
                                    'collection_id': collection_id.id if collection_id else False,
                                    'material_composition': Material_composition,
                                    'product_type_group_id': product_type_group_id.id if product_type_group_id else False,
                                    'age_group_id': age_group_id.id if age_group_id else False,
                                    'available_in_pos': Available_in_pos or False,
                                })
                                self.env.cr.commit()

                                new_variant_ids = new_template_id.product_variant_ids.filtered(
                                    lambda x: x.barcode == False and x.default_code == False)
                                if new_variant_ids:
                                    new_variant_ids.unlink()
                                    self.env.cr.commit()

                if template_id:
                    print("\ Cash-1")
                    # template_id.write(vals)
                    self.env.cr.commit()
                else:
                    print("\ Cash-2")
                    template_id = product_template_obj.with_context({
                        'skip_log': True
                        }).create(vals)
                    vals.update({
                        'nex_text_cells': Nex_text_cells,
                        'model_no': ModelNber,
                        'barcode': barcode,
                        'seasonality_id': seasonality_id.id if seasonality_id else False,
                        'collection_id': collection_id.id if collection_id else False,
                        'material_composition': Material_composition,
                        'product_type_group_id': product_type_group_id.id if product_type_group_id else False,
                        'age_group_id': age_group_id.id if age_group_id else False,
                        'available_in_pos': Available_in_pos or False
                    })
                    template_id.product_variant_ids[0].write(vals)
                    self.env.cr.commit()
                list_of_vals = []
                self.env.cr.commit()
                product_attribute_value = []
                """
                    If product product_variant_ids barcode is not found
                """
                if template_id.product_variant_ids.search([('barcode', '!=', barcode)]):
                    print ("641-------------------------")
                    for att in Attributes:
                        att_line_id = prod_tmpl_att_line_obj.search([
                            ('product_tmpl_id', '=', template_id.id),
                            ('attribute_id', '=', att.id)
                        ])
                        if att.name == 'Size' and V_Size:
                            V_Size_id = False
                            if isinstance(V_Size, float):
                                V_Size = str(int(V_Size))
                            V_Size_id = prod_att_value_obj.search([
                                ('name', '=', V_Size),
                                ('attribute_id', '=', att.id)
                            ], limit=1)
                            if not V_Size_id:
                                V_Size_id = prod_att_value_obj.with_context({
                                    'skip_log': True
                                }).create({
                                    'name': V_Size,
                                    'attribute_id': att.id
                                })
                            if att_line_id:
                                att_line_id.write({'value_ids': [(4, V_Size_id.id)]})
                                self.env.cr.commit()
                            else:
                                list_of_vals.append({
                                    'value_ids': [(4, V_Size_id.id)],
                                    'product_tmpl_id': template_id.id,
                                    'attribute_id': att.id
                                })
                            if V_Size_id:
                                product_attribute_value.append(V_Size_id.id)
                        if att.name == 'Color' and V_Color != 'unknowing':
                            V_Color_id = prod_att_value_obj.search([
                                ('name', '=', V_Color),
                                ('attribute_id', '=', att.id)
                                ], limit=1)
                            if not V_Color_id:
                                V_Color_id = prod_att_value_obj.with_context({
                                    'skip_log': True
                                    }).create({
                                        'name': V_Color,
                                        'attribute_id': att.id
                                    })
                            if att_line_id:
                                att_line_id.write({'value_ids': [(4, V_Color_id.id)]})
                                self.env.cr.commit()
                            else:
                                list_of_vals.append({
                                    'value_ids': [(4, V_Color_id.id)],
                                    'product_tmpl_id': template_id.id,
                                    'attribute_id': att.id
                                })
                            if V_Color_id:
                                V_Color_id = prod_att_value_obj.search([('name', '=', V_Color)], limit=1)
                                product_attribute_value.append(V_Color_id.id)
                if list_of_vals:
                    print("Call 578")
                    prod_tmpl_att_line_obj.with_context({
                        'skip_log': True
                    }).create(list_of_vals)
                    prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search([
                        ('product_tmpl_id', '=', template_id.id),
                        ('product_attribute_value_id', 'in', product_attribute_value)
                    ])
                    prod_verinet_ids = product_obj.search([
                        ('product_template_attribute_value_ids', 'in', prod_tmpl_att_value_ids.ids)
                    ])
                    prod_verinet_ids.write({
                        'standard_price': cost,
                        'barcode': barcode,
                        'available_in_pos': Available_in_pos or False
                    })
                    self.env.cr.commit()

                    variant_ids = template_id.product_variant_ids.filtered(
                        lambda x: x.barcode == False and x.default_code == False)
                    if variant_ids:
                        variant_ids.unlink()
                        self.env.cr.commit()

                else:

                    print("\ Cash-3", template_id.college_id, V_College_id.id)

                    if template_id.product_variant_ids and template_id.college_id.id == V_College_id.id:
                        if not product_obj.search([('barcode', '=', barcode)]) and not template_id.product_variant_ids[
                            -1].default_code:
                            print("Call 604")
                            template_id.product_variant_ids[-1].write({
                                'standard_price': cost,
                                'barcode': barcode,
                                'default_code': default_code,
                                'nex_text_cells': Nex_text_cells,
                                'model_no': ModelNber,
                                'available_in_pos': Available_in_pos or False,
                                'seasonality_id': seasonality_id.id if seasonality_id else False,
                                'collection_id': collection_id.id if collection_id else False,
                                'material_composition': Material_composition,
                                'product_type_group_id': product_type_group_id.id if product_type_group_id else False,
                                'age_group_id': age_group_id.id if age_group_id else False
                            })

                            prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search([
                                ('product_tmpl_id', '=', template_id.id),
                                ('product_attribute_value_id', 'in', product_attribute_value)
                            ])
                            if att_line_id:

                                existing_variant_ids = template_id.product_variant_ids[-1].product_template_attribute_value_ids

                                new_variant_ids = prod_tmpl_att_value_ids

                                product_ids = template_id.product_variant_ids
                                if existing_variant_ids != new_variant_ids:
                                    for rec in product_ids:
                                        if rec.product_template_attribute_value_ids == new_variant_ids:
                                            for variant in rec:
                                                template_id.product_variant_ids[-1].unlink()
                                                variant.update({
                                                    'standard_price': cost,
                                                    'barcode': barcode,
                                                    'default_code': default_code,
                                                    'nex_text_cells': Nex_text_cells,
                                                    'model_no': ModelNber,
                                                    'available_in_pos': Available_in_pos or False,
                                                    'seasonality_id': seasonality_id.id if seasonality_id else False,
                                                    'collection_id': collection_id.id if collection_id else False,
                                                    'material_composition': Material_composition,
                                                    'product_type_group_id': product_type_group_id.id if product_type_group_id else False,
                                                    'age_group_id': age_group_id.id if age_group_id else False,
                                                })
                                                print(f"Updated variant ID {variant.id} with new attribute values.")

                                self.env.cr.commit()

                            print("Variant updated with new attributes.")
                            self.env.cr.commit()

                self.env.cr.commit()
                # IF Diffrent Barcode and Same Internal Refreance
                find_template_id = template_id.product_variant_ids.filtered(
                    lambda x: x.barcode == barcode) and template_id.college_id.id == V_College_id.id
                # print("\n \n\n Cash-4 619", product_obj.search([('barcode', '=', barcode)]), template_id.college_id.id,  V_College_id.id)
                print("template_id", template_id)
                print("template_id.product_variant_ids", template_id.product_variant_ids)
                # print ("\n\n= = = = ", find_template_id, template_id.product_variant_ids.filtered(lambda x: x.barcode == barcode) and template_id.college_id.id == V_College_id.id)
                if not template_id.product_variant_ids.filtered(
                        lambda x: x.barcode == barcode) and not template_id.college_id.id == V_College_id.id:
                    """
                        new	old	old	old	new	creat new product template

                        When New barncode come and with Season
                    """
                    print("619")
                    new_template_id = product_template_obj.with_context({
                            'skip_log': True
                        }).create(vals)
                    product_attribute_value = []
                    for att in Attributes:
                        att_line_id = prod_tmpl_att_line_obj.search([
                            ('product_tmpl_id', '=', new_template_id.id),
                            ('attribute_id', '=', att.id)
                        ])
                        if att.name == 'Size' and V_Size:
                            V_Size_id = False
                            if isinstance(V_Size, float):
                                V_Size = str(int(V_Size))
                            V_Size_id = prod_att_value_obj.search([
                                ('name', '=', V_Size),
                                ('attribute_id', '=', att.id),
                            ])
                            if not V_Size_id:
                                V_Size_id = prod_att_value_obj.with_context({
                                    'skip_log': True
                                }).create({
                                    'name': V_Size,
                                    'attribute_id': att.id
                                })
                            if att_line_id:
                                att_line_id.write({'value_ids': [(4, V_Size_id.id)]})
                                self.env.cr.commit()
                            else:
                                list_of_vals.append({
                                    'value_ids': [(4, V_Size_id.id)],
                                    'product_tmpl_id': new_template_id.id,
                                    'attribute_id': att.id
                                })
                            if V_Size_id:
                                product_attribute_value.append(V_Size_id.id)
                        if att.name == 'Color' and V_Color != 'unknowing':
                            V_Color_id = prod_att_value_obj.search([
                                ('name', '=', V_Color),
                                ('attribute_id', '=', att.id),
                            ])
                            if not V_Color_id:
                                V_Color_id = prod_att_value_obj.with_context({
                                    'skip_log': True
                                }).create({
                                    'name': V_Color,
                                    'attribute_id': att.id
                                })
                            if att_line_id:
                                att_line_id.write({'value_ids': [(4, V_Color_id.id)]})
                                self.env.cr.commit()
                            else:
                                list_of_vals.append({
                                    'value_ids': [(4, V_Color_id.id)],
                                    'product_tmpl_id': new_template_id.id,
                                    'attribute_id': att.id
                                })
                            if V_Color_id:
                                product_attribute_value.append(V_Color_id.id)
                    if list_of_vals:
                        prod_tmpl_att_line_obj.with_context({
                                'skip_log': True
                            }).create(list_of_vals)
                        prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search([
                            ('product_tmpl_id', '=', new_template_id.id),
                            ('product_attribute_value_id', 'in', product_attribute_value)
                        ])
                        prod_verinet_ids = product_obj.search([
                            ('product_template_attribute_value_ids', 'in', prod_tmpl_att_value_ids.ids)
                        ])
                        prod_verinet_ids.write({
                            'standard_price': cost,
                            'barcode': barcode,
                            'nex_text_cells': Nex_text_cells,
                            'model_no': ModelNber,
                            'barcode': barcode,
                            'default_code': default_code,
                            'seasonality_id': seasonality_id.id if seasonality_id else False,
                            'collection_id': collection_id.id if collection_id else False,
                            'material_composition': Material_composition,
                            'product_type_group_id': product_type_group_id.id if product_type_group_id else False,
                            'age_group_id': age_group_id.id if age_group_id else False,
                            'available_in_pos': Available_in_pos or False,
                        })
                        self.env.cr.commit()

                        # new_variant_ids = new_template_id.product_variant_ids.filtered(lambda x: x.barcode == False and x.default_code == False)
                        # if new_variant_ids:
                        #     new_variant_ids.unlink()
                        #     self.env.cr.commit()
                elif not template_id.product_variant_ids.filtered(lambda x: x.barcode == barcode):
                    print("710")
                    """ new	when add nerw attbuits in templat the system take 
                        Attributes that creat it first (ID of Attributes) as 
                        probality for ech product	old	old	old	add the product for sam templeat	"""
                    prod_tmpl_att_line_obj.with_context({
                            'skip_log': True
                        }).create(list_of_vals)
                    prod_tmpl_att_value_ids = prod_tmpl_att_value_obj.search([
                        ('product_tmpl_id', '=', template_id.id),
                        ('product_attribute_value_id', 'in', product_attribute_value)
                    ])
                    prod_verinet_ids = product_obj.search([
                        ('product_template_attribute_value_ids', 'in', prod_tmpl_att_value_ids.ids)
                    ])
                    # prod_verinet_ids.write({
                    #     'standard_price': cost,
                    #     'barcode': barcode,
                    # })
                    self.env.cr.commit()
                    variant_ids = template_id.product_variant_ids.filtered(
                        lambda x: x.barcode == False and x.default_code == False)
                    if variant_ids:
                        variant_ids.unlink()
                    self.env.cr.commit()

                variant_ids = template_id.product_variant_ids.filtered(
                    lambda x: x.barcode == False and x.default_code == False)
                if variant_ids:
                    variant_ids.unlink()
                    self.env.cr.commit()
                count += 1
                _logger.info("/n/n/n/n/n/n====RECORD Genrater =========%s" % (str(count)))
                T_count += 1
                if limit == count:
                    _logger.info("/n/n/n/n/n/n============================%s" % (str(T_count)))
                    time.sleep(5)
                    count = 1
            new_cr.close()
