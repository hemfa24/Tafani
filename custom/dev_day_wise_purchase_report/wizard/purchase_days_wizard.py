# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields
from odoo.tools.misc import xlwt, str2bool
from io import BytesIO
from xlwt import easyxf
import base64
import time
from datetime import date, datetime
import xlsxwriter
from xlwt import easyxf, Formula


class PurchaseDayWise(models.TransientModel):

    _name ='purchase.days.wizard'

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date', required=True)
    company_ids = fields.Many2many('res.company', string='Companies')
    print_in_draft = fields.Boolean(string='Print Draft')
    
    def get_day_number(self, product_id, day):
        purchase_line = self.env['purchase.order.line'].search([('order_id.date_order', '>=', self.start_date),
                                                        ('order_id.date_order', '<=', self.end_date),
                                                        ('product_id', '=', product_id)
                                                        ])
        number = 0
        for line in purchase_line:
            days = line.order_id.date_order.strftime("%A")
            if days == day:
                number += 1
        return int(number)
    
    
    
    def print_excel_report(self):
        filename = 'Excel Purchase Report.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Excel Report')
        worksheet.show_grid = False
        
        domain = ('state','in',['done','purchase'])
        if self.print_in_draft:
            domain = ('state','in',['draft','done','purchase'])
            
        purchase_line = self.env['purchase.order.line'].search([('order_id.date_order', '>=', self.start_date),('order_id.date_order', '<=', self.end_date),('order_id.company_id', 'in', self.company_ids.ids),domain])
        for purchase in self.company_ids:
            company = purchase.name
        
# defining various font styles
        
        header_style = easyxf('font:height 400; align: horiz center;font:bold True;')
        style = easyxf('font:height 200; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;')
        style_h = easyxf('font:height 200; align: horiz center;font:bold True; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;')
        sub_header_t = easyxf('font:height 500;align: horiz center;pattern: pattern solid, fore_color silver_ega;font:bold True;''borders: top thin,bottom thin,left thin, right thin')
        content = easyxf('font:height 200;')
        content_border = easyxf('font:height 200;''borders: top_color black, bottom_color black, right_color black, left_color black,top thin,bottom thin,left thin, right thin;')
        content_border_c = easyxf('font:height 200;''borders:top thin,bottom thin,left thin, right thin;')
        content_border_center = easyxf('font:height 200;''borders:top_color black, bottom_color black, right_color black, left_color black, top thin,bottom thin,left thin, right thin; align: horiz center;')
        sub_header = easyxf('font:height 210;align: horiz center;pattern: pattern solid, fore_color silver_ega;font:bold True;''borders: top thin,bottom thin,left thin, right thin')
        
        sub_header_c = easyxf('font:height 210;align: horiz center;pattern: pattern solid, fore_color silver_ega;font:bold True;''borders: top_color black, bottom_color black, right_color black, left_color black,top thin,bottom thin,left thin, right thin')

# setting with of the column

        worksheet.col(1).width = 6000
        worksheet.col(2).width = 2500
        worksheet.col(3).width = 2500
        worksheet.col(4).width = 3000
        worksheet.col(5).width = 2500
        worksheet.col(6).width = 2500
        worksheet.col(7).width = 2500
        worksheet.col(8).width = 3000

# setting with of the Row

        for i in range(26):
            worksheet.row(i).height = 350
            
        worksheet.write_merge(2, 3, 1, 9, 'Purchase Days Wise Report',sub_header_t)
       
# Header Tital Print

        worksheet.write(5, 1, 'Start Date',sub_header_c)
        worksheet.write_merge(5,5, 6,7, 'End Date',sub_header_c)
        worksheet.write(7, 1, 'Company',sub_header_c)

# Line Tital Print
        
        worksheet.write(10, 1, 'Product Name',sub_header_c)
        worksheet.write(10, 2, 'Monday',sub_header_c)
        worksheet.write(10, 3, 'Tuesday',sub_header_c)
        worksheet.write(10, 4, 'Wednesday',sub_header_c)
        worksheet.write(10, 5, 'Thursday',sub_header_c)
        worksheet.write(10, 6, 'Friday',sub_header_c)
        worksheet.write(10, 7, 'Saturday',sub_header_c)
        worksheet.write(10, 8, 'Sunday',sub_header_c)
        worksheet.write(10, 9, 'Total',sub_header_c)

# Header Details Print

        s_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        worksheet.write_merge(5,5,2, 3, s_date,style_h)         
        e_date = datetime.strptime(str(self.end_date), "%Y-%m-%d").strftime('%d-%m-%Y')
        worksheet.write_merge(5,5,8, 9, e_date,style_h)
        worksheet.write_merge(7,7,2, 4, company,style_h)
        

#Line Details Print
        
        final_list = []
        product_data = []
        counter =11
        total_col=0
        
        for line in purchase_line:
            
            if line.product_id.id not in product_data:
                product_data.append(line.product_id.id)
                
                worksheet.write(counter, 1, line.product_id.name,style)
                worksheet.write(counter, 2, self.get_day_number(line.product_id.id,'Monday'),style)
                worksheet.write(counter, 3, self.get_day_number(line.product_id.id,'Tuesday'),style)
                worksheet.write(counter, 4, self.get_day_number(line.product_id.id,'Wednesday'),style)
                worksheet.write(counter, 5, self.get_day_number(line.product_id.id,'Thursday'),style)
                worksheet.write(counter, 6, self.get_day_number(line.product_id.id,'Friday'),style)
                worksheet.write(counter, 7, self.get_day_number(line.product_id.id,'Saturday'),style)
                worksheet.write(counter, 8, self.get_day_number(line.product_id.id,'Sunday'),style)
                worksheet.write(counter,9, Formula('SUM(C'+str(counter+1)+':I'+str(counter+1)+')'),style)
                counter+=1
                
        worksheet.write(counter,1, 'Total', sub_header_c)
        worksheet.write(counter,2, Formula('SUM(C'+str(12)+':C'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,3, Formula('SUM(D'+str(12)+':D'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,4, Formula('SUM(E'+str(12)+':E'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,5, Formula('SUM(F'+str(12)+':F'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,6, Formula('SUM(G'+str(12)+':G'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,7, Formula('SUM(H'+str(12)+':H'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,8, Formula('SUM(I'+str(12)+':I'+str(counter)+')'), sub_header_c)
        worksheet.write(counter,9, Formula('SUM(J'+str(12)+':J'+str(counter)+')'), sub_header_c)          
        counter+=1 
                
                
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})
        active_id = self.ids[0]
        url = ('web/content/?model=purchase.days.wizard&download=true&field=excel_file&id=%s&filename=%s' % (active_id, filename))
        if self.excel_file:
            return {'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new'
                    }


    excel_file = fields.Binary(string='Excel File')

    def print_report(self):
        data = self.read()
        datas = {'form': self.id}
        return self.env.ref('dev_day_wise_purchase_report.wizard_menu_purchase_day').report_action(self, data=datas)  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
