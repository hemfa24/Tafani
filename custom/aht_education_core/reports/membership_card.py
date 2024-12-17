from odoo import models,api,fields,tools,_


from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError


class MemberLibraryCard(models.AbstractModel):
    _name="report.aht_education_core.report_membership_card"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        
        rec_model = self.env['res.partner'].browse(docids)
        
        
        return {
            'doc_ids': self.ids,
            'rec':rec_model,
            'data':data,
            'company':self.env.company
           
            
        }