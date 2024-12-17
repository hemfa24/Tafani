from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError
import datetime
import io
import base64
try:
    import xlwt
except ImportError:
    xlwt = None


class Top_Growing_Product(models.TransientModel):
    _name = "sale.margin"
    _description="Top Growing Product"

    from_date = fields.Date(string="From Date",required=True)
    to_date = fields.Date(string="To Date",required=True)
    product_ids = fields.Many2many('product.product','rel_product_product_margin',string="Products")
    company_ids = fields.Many2many('res.company','rel_company_ids_margin',string="Company")
    warehouse_ids = fields.Many2many('stock.warehouse','rel_stock_warehouse_margin_id',string="Warehouse")
    partner_ids = fields.Many2many('res.partner','rel_partner_ids_margin',string="Customers")
    sales_person_ids = fields.Many2many('res.users','rel_users_ids_margin',string="Salesperson")
    
    negative_margin_highlight = fields.Boolean(string="Negative Margin Highlight")
    sales_channel_ids = fields.Many2many('crm.team','rel_crm_team_margin',string="Sales Channel")



    @api.constrains('from_date','from_date')
    def check_dates(self):
        if self.from_date > self.to_date:
            raise UserError(_('To Date should be after the To Date!!') )


    def print_pdf_report(self):


        return self.env.ref('bi_sale_margin_report.sales_margin_report_pdf').report_action(self)


    def get_lines(self):
        vals = []
        domain = []
        sale_order_obj = self.env['sale.order']

        if self.company_ids :
            domain.append(('company_id','in',self.company_ids.ids))
        if self.warehouse_ids :
            domain.append(('warehouse_id','in',self.warehouse_ids.ids))
        if self.sales_person_ids : 
            domain.append(('user_id','in',self.sales_person_ids.ids))
        if self.sales_channel_ids :
            domain.append(('team_id','in',self.sales_channel_ids.ids))
        # if self.from_date :
        #
        #     domain.append(('confirmation_date','>=',self.from_date))
        # if self.to_date :
        #     domain.append(('confirmation_date','<=',self.to_date))
        domain.append(('state', 'in', ('sale', 'done')))
        if self.partner_ids :
            domain.append(('partner_id','in',self.partner_ids.ids))

        
        sale_orders = sale_order_obj.search(domain)
        for sale in sale_orders :
            
            for line in sale.order_line :
                if self.product_ids :
                    if line.product_id.id in self.product_ids.ids :
                        
                        disscount_amount = (line.price_unit * line.product_uom_qty * line.discount)/100
                        
                        untaxed_sale = (line.price_unit * line.product_uom_qty) - disscount_amount
                        margin_amount = untaxed_sale - (line.product_id.standard_price * line.product_uom_qty)
                        margin_percentage = (margin_amount/(untaxed_sale or 1)) * 100
                        vals.append({
                            'sale_order': sale.name,
                            'product_name' :line.product_id.name,
                            'date': sale.date_order,
                            'customer' : sale.partner_id.name,
                            'warehouse' :sale.warehouse_id.name,
                            'team' : sale.team_id.name,
                            'salesperson': sale.user_id.name,
                            'company' : sale.company_id.name,
                            'cost' : line.product_id.standard_price * line.product_uom_qty,
                            'untaxed_sale' : untaxed_sale,
                            'discount' : disscount_amount,
                            'margin_amount':margin_amount,
                            'margin_percentage' :round(margin_percentage, 2),
                            })
                else :


                    disscount_amount = (line.price_unit * line.product_uom_qty * line.discount)/100
                        
                    untaxed_sale = (line.price_unit * line.product_uom_qty) - disscount_amount
                    margin_amount = untaxed_sale - (line.product_id.standard_price * line.product_uom_qty)
                    margin_percentage = (margin_amount/(untaxed_sale or 1)) * 100
                    vals.append({
                            'sale_order': sale.name,
                            'product_name' :line.product_id.name,
                            'date': sale.date_order,
                            'customer' : sale.partner_id.name,
                            'warehouse' :sale.warehouse_id.name,
                            'team' : sale.team_id.name,
                            'salesperson': sale.user_id.name,
                            'company' : sale.company_id.name,
                            'cost' : line.product_id.standard_price * line.product_uom_qty,
                            'untaxed_sale' : untaxed_sale,
                            'discount' : disscount_amount,
                            'margin_amount':margin_amount,
                            'margin_percentage' :round(margin_percentage, 2),
                            })
             
        return vals


    def print_xls_report(self):
        filename = 'Sale Margin.xls'
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        fontP = xlwt.Font()
        fontP.bold = True
        fontP.height = 200
        stylePC.font = fontP
        stylePC.num_format_str = '@'
        stylePC.alignment = alignment
        style_title = xlwt.easyxf("font:height 200;pattern: pattern solid, pattern_fore_colour gray25; font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet = workbook.add_sheet('Sheet 1')
        margin_style = xlwt.easyxf("font: name Liberation Sans,color red;")
        title = "Sale Margin Report"
        worksheet.write(1, 3,'Date From:',style_table_header)
        worksheet.write(1, 4,str(self.from_date),style_table_header)
        worksheet.write(1, 10,'Date To:',style_table_header,)
        worksheet.write(1, 11,str(self.to_date),style_table_header)
        
        worksheet.write_merge(5, 5, 1, 13, title, style=style_title)
        
        worksheet.write(6, 1, 'Sale Order', style_title)
        worksheet.write(6, 2, 'Product Name', style_title)
        worksheet.write(6, 3, 'Date', style_title)
        worksheet.write(6, 4, 'Customer', style_title)
        worksheet.write(6, 5, 'Warehouse', style_title)
        worksheet.write(6, 6, 'Team', style_title)
        worksheet.write(6, 7, 'SalesPerson', style_title)
        worksheet.write(6, 8, 'Company', style_title)
        worksheet.write(6, 9, 'Cost', style_title)
        worksheet.write(6, 10, 'Untaxed Sale', style_title)
        worksheet.write(6, 11, 'Discount Amount', style_title)
        worksheet.write(6, 12, 'Margin Amount', style_title)
        worksheet.write(6, 13, 'Margin Percentage', style_title)
        
        lines = self.get_lines()
        row = 7
        clos = 0
        if self.negative_margin_highlight == True : 
            for line in lines :
                if line['margin_percentage'] < 0 :
                    worksheet.write(row, 1,line['sale_order'],margin_style)
                    worksheet.write(row, 2,line['product_name'],margin_style)
                    worksheet.write(row, 3,str(line['date']),margin_style)
                    worksheet.write(row, 4,line['customer'],margin_style)
                    worksheet.write(row, 5,line['warehouse'],margin_style)
                    worksheet.write(row, 6,line['team'],margin_style)
                    worksheet.write(row, 7,line['salesperson'],margin_style)
                    worksheet.write(row, 8,line['company'],margin_style)
                    worksheet.write(row, 9,line['cost'],margin_style)
                    worksheet.write(row, 10,line['untaxed_sale'],margin_style)
                    worksheet.write(row, 11,line['discount'],margin_style)
                    worksheet.write(row, 12,line['margin_amount'],margin_style)
                    worksheet.write(row, 13,line['margin_percentage'],margin_style)


                else :
                    worksheet.write(row, 1,line['sale_order'])
                    worksheet.write(row, 2,line['product_name'])
                    worksheet.write(row, 3,str(line['date']))
                    worksheet.write(row, 4,line['customer'])
                    worksheet.write(row, 5,line['warehouse'])
                    worksheet.write(row, 6,line['team'])
                    worksheet.write(row, 7,line['salesperson'])
                    worksheet.write(row, 8,line['company'])
                    worksheet.write(row, 9,line['cost'])
                    worksheet.write(row, 10,line['untaxed_sale'])
                    worksheet.write(row, 11,line['discount'])
                    worksheet.write(row, 12,line['margin_amount'])
                    worksheet.write(row, 13,line['margin_percentage'])
                
                row = row+1
        else : 
            for line in lines :
             
                worksheet.write(row, 1,line['sale_order'])
                worksheet.write(row, 2,line['product_name'])
                worksheet.write(row, 3,str(line['date']))
                worksheet.write(row, 4,line['customer'])
                worksheet.write(row, 5,line['warehouse'])
                worksheet.write(row, 6,line['team'])
                worksheet.write(row, 7,line['salesperson'])
                worksheet.write(row, 8,line['company'])
                worksheet.write(row, 9,line['cost'])
                worksheet.write(row, 10,line['untaxed_sale'])
                worksheet.write(row, 11,line['discount'])
                worksheet.write(row, 12,line['margin_amount'])
                worksheet.write(row, 13,line['margin_percentage'])
                
                row = row+1
        
        fp = io.BytesIO()
        workbook.save(fp)
        
        export_id = self.env['sale.margin.report.excel'].create({'excel_file': base64.b64encode(fp.getvalue()), 'file_name': filename})
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'sale.margin.report.excel',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target':'new'
                }
        return res




class Sales_Margin_report_excel(models.TransientModel):
    _name = "sale.margin.report.excel"
    _description="Sale Margin Report Excel"

    excel_file = fields.Binary('Excel Report Sale Margin')
    file_name = fields.Char('Excel File', size=64)
