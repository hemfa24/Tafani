from odoo import fields, models,_,api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning,UserError


class CRMLead(models.Model):
    _inherit = "crm.lead"
    
    @api.model
    def create(self, vals):
        res = super(CRMLead, self).create(vals)
        if res.stage_id.field_template_id:
            field_list = ''
            for template in res.stage_id.field_template_id:
                for lead_field in template.field_ids:
                    domain = [('id','=',res.id),(lead_field.name,'=',False)]
                    crm_id = self.env['crm.lead'].sudo().search(domain)
                    if crm_id.id == res.id:
                        if field_list:
                            field_list = '%s,%s' %(field_list,lead_field.field_description)
                        else:
                            field_list = '%s' %(lead_field.field_description)
            if field_list and not self.env.context.get('import_file'):
                raise UserError(_("Please provide value %s to process"%(field_list)))
        return res
    
    def write(self, values):
        if 'stage_id' in values:
            stage_id = self.env['crm.stage'].sudo().browse(values['stage_id'])
            if stage_id.field_template_id:
                field_list = ''
                for template in stage_id.field_template_id:
                    for lead_field in template.field_ids:
                        domain = [('id','=',self.id),(lead_field.name,'=',False)]
                        crm_id = self.env['crm.lead'].sudo().search(domain)
                        if crm_id.id == self.id:
                            if field_list:
                                field_list = '%s,%s' %(field_list,lead_field.field_description)
                            else:
                                field_list = '%s' %(lead_field.field_description)
                if field_list and not self.env.context.get('import_file'):
                    raise UserError(_("Please provide value %s to process"%(field_list)))
                    
        return super(CRMLead, self).write(values)