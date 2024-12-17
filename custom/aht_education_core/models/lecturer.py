from odoo import api, fields, models, _
from lxml import etree

class Lecturer(models.Model):
    _inherit = 'hr.employee'

    is_lecturer= fields.Boolean()
    user_created = fields.Boolean(default= False ,compute="isUserCreated")
    
    @api.depends('user_id')
    def isUserCreated(self):
        for res in self:
            if res.user_id:
                res.user_created = True
            else: 
                res.user_created = False
    
    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('default_is_lecture',False):
            vals_list[0]['is_lecture'] = True
        res= super(Lecturer ,self).create(vals_list)
        return res
    
    def btn_create_user(self):
        if not self.user_id:
            record =  self.env['res.users'].sudo().create({
                    'login': self.name,
                    'email': self.work_email,
                    'name': self.name,
                    'image_1920': self.image_1920,
                    'company_id': self.company_id.id
                })
            lecturer_group_id = self.env.ref('aht_education_core.group_lecturer')
            lecturer_group_id.write({'users': [(4, record.id)]})
            self.user_id= record.id
            print(f'record {record.id} created!')
    
    
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(Lecturer,self).get_view(view_id, view_type, **options) 
        if self.env.user.has_group('aht_education_core.group_lecturer'):
            temp = etree.fromstring(result['arch'])
            temp.set('create', '0')
            temp.set('edit', '0')
            temp.set('delete', '0')
            result['arch'] = etree.tostring(temp)
       
        return result        

    