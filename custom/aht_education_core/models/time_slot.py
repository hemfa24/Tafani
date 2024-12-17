from odoo import api, fields, models, _
import datetime

class TimeSlots(models.Model):
    _name = 'time.slot'
    
    
    name= fields.Char(
        string="Time slot",
        required=True, copy=False, readonly=True,
       
       
        default=lambda self: _('New'))
    start_time = fields.Float(
        "Start Time",
        required=True,
        help="Time according to timeformat of 24 hours",
    )
    end_time = fields.Float(
        "End Time",
        required=True,
        help="Time according to timeformat of 24 hours",
    )
    
    def floatToTime(self, val):
        minutes =float(val)*60
        hours, minutes = divmod(minutes, 60)
        c_time = "%02d:%02d"%(hours, round(minutes,2))
        return c_time
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                st_time  = self.floatToTime(vals['start_time']) 
                end_time = self.floatToTime(str(vals['end_time'])) 
                vals['name'] =str(st_time) +"-"+str(end_time)  or _('New')
        res = super(TimeSlots, self).create(vals_list)
        return res
    
    
    
    def write(self, vals):
        print(vals)
        if 'end_time' in vals  or 'start_time' in vals:
            if  'end_time' in vals:
                end_time = self.floatToTime(str(vals['end_time']))
                st_time  = self.floatToTime(self.start_time)
                self.name =  str(st_time) +"-"+str(end_time)
                 
            if  'start_time' in vals:
                st_time  = self.floatToTime(str(vals['start_time']))
                end_time =  self.floatToTime(self.end_time)
                self.name =  str(st_time) +"-"+str(end_time) 
                
        if 'end_time' in vals  and 'start_time' in vals: 
                st_time  = self.floatToTime(str(vals['start_time']))    
                end_time = self.floatToTime(str(vals['end_time']))
                self.name =  str(st_time) +"-"+str(end_time)
                
        res = super(TimeSlots, self).write(vals)
        return res 
         
         
         