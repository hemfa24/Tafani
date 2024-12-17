from odoo import models, fields, api,tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime,date,timedelta



class IssueBookTransaction(models.Model):
    _name="aht.issue.book"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    
    name= fields.Char(
        string="book issue number                                                                                     ",
        required=True, copy=False, readonly=True,
        default=lambda self: _('New'))
    
    inv_flag = fields.Boolean(string="Invoice Flag" , default=False)
    partner_id = fields.Many2one("res.partner",string="Member" ,required=True)
    book_name= fields.Many2one('product.product', string = "Book Name" ,required=True)
    book_tmpl_id= fields.Many2one('product.template', string = "Book Name")
    due_date = fields.Date(string="Due Date", readonly=True, store=True)
    fine_amount = fields.Float(string="Fine Amount" ,readonly = True)
    renewd_count = fields.Integer(string="Renewd Count")
    copy_barcode = fields.Char(string="Copy barcode",required=True)
    book_issue_date = fields.Date(string="Book Issue Date" ,default=datetime.today())
    responsible_id=  fields.Many2one("res.users",string="Responsible", default= lambda self:self.env.user,required=True)
    state =  fields.Selection(
        selection=[
            ('Draft', "Draft"),
            ('Issued', "Issued"),
            ('Returned', "Returned"),
            
       ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='Draft')
    
    book_issue_id = fields.Many2one("aht.issue.book" ,string= "book issue id") 
    invoice_id= fields.Many2one("account.move", readonly="True")
    
    
    
    def updateRenew(self,record):
        issue_book_record = self.env['aht.issue.book'].browse([record])
        renew_count = issue_book_record.renewd_count  if issue_book_record.renewd_count else 0
        allowedDays= 0
        allowedDaysConfig =self.env['ir.config_parameter'].sudo().get_param('aht_education_core.allowed_days')
        if allowedDaysConfig:
            allowedDays = int(allowedDaysConfig)
        due_date_extnd = issue_book_record.due_date + timedelta(days= int(allowedDays))  
        issue_book_record.update({'renewd_count':renew_count+1,
                                  'due_date':due_date_extnd})
        res_data={'renew_count':issue_book_record.renewd_count,
                'due_date':issue_book_record.due_date}
        return res_data
        
    
    @api.onchange('book_issue_date')
    def get_due_date(self):
        
        allowedDays= 0
        allowedDaysConfig =self.env['ir.config_parameter'].sudo().get_param('aht_education_core.allowed_days')
        if allowedDaysConfig:
            allowedDays = allowedDaysConfig
        for res in self:
            if res.book_issue_date:
                issue_date = res.book_issue_date
            else:
                issue_date=  datetime.now().date()    
            allowed_days= issue_date +timedelta(days= int(allowedDays))
            res.due_date =allowed_days
            
    
    
    
    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for template in self:
            template.can_image_1024_be_zoomed = template.image_1920 and tools.is_image_size_above(template.image_1920, template.image_1024)
    
    def get_book_tmpl(self,res):
        prd_name=res.book_name.name.split("(")[0]
        prd_id=self.env['product.template'].search([('name','=',prd_name)])
        if prd_id:
            return prd_id
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            prd_tmpl= self.env['product.product'].browse([vals.get('book_name')]).product_tmpl_id
            book_copy_status = prd_tmpl.book_copy_line_ids.mapped('status')
            if not 'Available' in book_copy_status:
                raise ValidationError(_('Book not Available'))
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('aht.book.issue') or _('New')
        res = super(IssueBookTransaction, self).create(vals_list)
        # book_tmpl_id = self.get_book_tmpl(res) 
        # if book_tmpl_id:
        #     res.update({'book_tmpl_id':book_tmpl_id.id})
        return res 
    
    def button_issue(self):
        # try:
        self.book_name.status = 'Checked out'
        book_copy_id= self.env['book.copies'].search([('product_tmpl_id','=',self.book_name.product_tmpl_id.id),('book_barcode','=',self.copy_barcode)])
        if book_copy_id:
            book_copy_id.status ='Checked out'
        else:
            raise UserError(_("Please enter correct barcode"))   
        self.write({'state':'Issued'})  
        self.book_name.product_tmpl_id.issue_book_ids += self
        # except Exception as e:
        #     print(e.args)
        
        
    def button_return(self):
        self.write({'state':'Returned'}) 
        
    def btn_openFeeWiz(self):
        
        try:
            action = self.env["ir.actions.actions"]._for_xml_id('aht_education_core.action_wizard_fee')
            fine_per_day = self.env['ir.config_parameter'].sudo().get_param('aht_education_core.fine_per_day')
            fee_multiple = self.env['ir.config_parameter'].sudo().get_param('aht_education_core.fee_multiple')
            item_fee=0.0
            if fine_per_day and fee_multiple:
                item_fee = float(fine_per_day) * int(fee_multiple)
            context = {'default_issue_book_id': self.id,
                       'default_item_fee':item_fee}
            action['context'] = context
            return action
        except Exception as e:
            print(e.args)
        
        
                       
    