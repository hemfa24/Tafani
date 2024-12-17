from odoo import fields, models,_,api
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning



class RequiredFieldTemplate(models.Model):
    _name = "required.field.template"
    _description = "Required Field Template"
    
    name = fields.Char('Name')
    required_customer = fields.Boolean('Required Customer')
    field_ids = fields.Many2many('ir.model.fields',string="Fields",domain="[('model_id.model','=','crm.lead')]")