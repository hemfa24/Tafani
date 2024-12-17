from odoo import fields, models,_,api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning



class CRMStage(models.Model):
    _inherit = "crm.stage"
    
    field_template_id = fields.Many2many('required.field.template',string="Field Template")