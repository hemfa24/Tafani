# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api
from datetime import datetime




class sales_margin_report(models.AbstractModel):
    _name = 'report.bi_sale_margin_report.sales_margin_template'
    _description="Sale Margin Report"

    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        docs = self.env['sale.margin'].browse(docids)
        data  = { 'from_date': docs.from_date, 'to_date': docs.to_date,
        'product_ids':docs.product_ids,
        'company_ids' : docs.company_ids,
        'warehouse_ids' : docs.warehouse_ids,
        'partner_ids' : docs.partner_ids,
        'sales_person_ids' : docs.sales_person_ids,
        'negative_margin_highlight': docs.negative_margin_highlight,
        'sales_channel_ids' : docs.sales_channel_ids,
        }
        
        return {
                   'doc_model': 'sale.margin',
                   'data' : data,

                   
                   'get_lines':self._get_lines(data),
                   
                   }


    def _get_lines(self,data):


        vals = []
        domain = []

        sale_order_obj = self.env['sale.order']

        if data['company_ids'] :
            domain.append(('company_id','in',data['company_ids'].ids))
        if data['warehouse_ids'] :
            domain.append(('warehouse_id','in',data['warehouse_ids'].ids))
        if data['sales_person_ids'] :
            domain.append(('user_id','in',data['sales_person_ids'].ids))
        if data['sales_channel_ids'] : 
            domain.append(('team_id','in',data['sales_channel_ids'].ids))
        if data['from_date'] :
            domain.append(('date_order','>=',data['from_date']))
        if data['to_date'] :
            domain.append(('date_order','<=',data['to_date']))

        domain.append(('state', 'in', ('sale', 'done')))
        if data['partner_ids'] :
            domain.append(('partner_id','in',data['partner_ids'].ids))

        
        sale_orders = sale_order_obj.search(domain)
        

        for sale in sale_orders :
            
            for line in sale.order_line :
                if data['product_ids'].ids :
                    if line.product_id.id in data['product_ids'].ids :
                        
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