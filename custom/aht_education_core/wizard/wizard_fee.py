from odoo import models, fields, api, _, tools,exceptions
from datetime import datetime, timezone

class WizItemFee(models.TransientModel):
    _name="wizard.fee"
    
    item_fee = fields.Float(string="Lost Item fee" ,readonly=True)
    inv_payment =fields.Float(string="Payment" ,readonly=False)
    
    def createInv(self,rec):
        invoice_vals_list=[]
        lib_product = self.env['product.product'].search([('name','=','Product Library Fine')])
        invoice_vals_list.append({
                                        'product_id':lib_product.id,
                                        'name': rec.book_name.name,
                                        'price_unit':self.inv_payment,
                                        'quantity': 1,
                                     })  
                                        # 'account_id':ag_bill.product_id.categ_id.property_account_expense_categ_id.id })
                                   
        invoice_id =self.env['account.move'].create({
                    'partner_id':rec.partner_id.id,
                    'move_type' : 'out_invoice',
                    'invoice_date':rec.due_date,
                    'invoice_line_ids': [(0, 0,l ) for l in invoice_vals_list],                               
                 })
        return invoice_id
    def confirm_fee(self):
        rec_id=   self.env.context.get('default_issue_book_id')
        book_issue_id = self.env['aht.issue.book'].browse([rec_id])
        invoice_id = self.createInv(book_issue_id) 
        book_issue_id.update({'fine_amount':self.item_fee,
                              'inv_flag':True,
                              'invoice_id':invoice_id.id})
        book_copy_id= self.env['book.copies'].search([('product_tmpl_id','=',book_issue_id.book_name.product_tmpl_id.id),('book_barcode','=',book_issue_id.copy_barcode)])
        book_copy_id.status= 'Lost'
        
        print("btn")