from odoo import models, fields, api,_
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError


class eduAttendanceSettings(models.TransientModel):
    _inherit="res.config.settings"
    
    attendance_types =  fields.Selection(
        selection=[
            ('Hourly', "Hourly"),
            ('Present/Absent', "Present/Absent"),
       ],
        string="Attendance type",
        
        default='Hourly',
        config_parameter='aht_education_core.attendance_type')
       
    fine_per_day = fields.Float(string="Fine per Day")
    fee_multiple =  fields.Integer(string="Lost Item fee multiple")
    allowed_days =fields.Integer(string="Book Allowed days")
    
    def set_values(self):
        super(eduAttendanceSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param('aht_education_core.attendance_types',
                                self.attendance_types)
       
        IrConfigPrmtr.set_param('aht_education_core.fine_per_day',
                                self.fine_per_day)
   
        IrConfigPrmtr.set_param('aht_education_core.fee_multiple',
                                self.fee_multiple)
        
        
        IrConfigPrmtr.set_param('aht_education_core.allowed_days',
                                self.allowed_days)
    @api.model
    def get_values(self):
        res = super(eduAttendanceSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        
        attendance_type = IrConfigPrmtr.get_param('aht_education_core.attendance_types')
        fine_per_day = IrConfigPrmtr.get_param('aht_education_core.fine_per_day')  
        fee_multiple =IrConfigPrmtr.get_param('aht_education_core.fee_multiple')  
        allowed_days =IrConfigPrmtr.get_param('aht_education_core.allowed_days')
          
        res.update({
            'attendance_types': attendance_type,
            'fine_per_day': fine_per_day,
            'fee_multiple': fee_multiple,
            'allowed_days':allowed_days
            })
        return res
   
    #
    #
    # def set_values(self):
    #     super(eduAttendanceSettings, self).set_values()
    #     company_id = self.env.user.company_id
    #     company_id.attendance_type = self.attendance_type
    #
    #
    # def get_values(self):
    #     res = super(eduAttendanceSettings, self).get_values()
    #     res.update(
    #         attendance_type = self.env.user.company_id.attendance_type
    #
    #     )
    #     return res
        
    
# class ResCompanySettings_inh(models.Model):
#     _inherit = 'res.company'
#
#
#
#     attendance_type =  fields.Selection(
#         selection=[
#             ('hourly', "Hourly"),
#             ('Present/Absent', "Present/Absent'"),
#        ],
#         string="Attendance type",
#
#         default='')

