from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class ReportTimeTable(models.AbstractModel):
    _name = 'report.aht_education_core.timetable_report_pdf'
    
    
    def GetTimeSlot(self):
        time_obj = self.env['time.slot'].search([])
        sorted_time_obj = time_obj.sorted(key='start_time')
        time_list = sorted_time_obj.mapped('start_time')
        str_timelist = list(map(time_obj.floatToTime, time_list))
        return time_list,str_timelist
        
        
        
    def floatToTime(self, val):
        minutes =float(val)*60
        hours, minutes = divmod(minutes, 60)
        c_time = "%02d:%02d"%(hours, round(minutes,2))
        return c_time
        
    def getTimeDayRecord(self,weekday,st_time, records):
        weekday = weekday.lower() 
        new_recs = records.filtered(lambda r, d=weekday, t=st_time: r.week_day == d and r.time_slot.start_time == t )
        
        return new_recs
    
       
    @api.model
    def _get_report_values(self, docids, data=None):
        print(data)
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        weekday_list=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        time_list,str_timelist = self.GetTimeSlot()
        records= self.env['class.timetable.line'].search([('timetable_id.academic_year','=',rec.academic_year.id)])
        if rec.type == 'class':
            records=  records.filtered(lambda r,clas= rec.class_id.id : r.timetable_id.class_id.id == clas)
        
        if rec.type == 'lecturer':
            records=  records.filtered(lambda r,lecturer = rec.lecturer_id.id : r.lecturer_id.id == lecturer)
        
        if rec.type == 'room':
            records=  records.filtered(lambda r,room = rec.class_room_id.id : r.class_room_id.id == room)
        
        if not len(records) > 0:
            raise UserError(_('No data found!')) 
        
        
        return {
            'docs' : docids,
            'data' : rec,
            'records':records,
            'weekday_lst':weekday_list,
            'time_list':time_list,
            'func_floatToTime':self.floatToTime,
            'getTimeDayRecord': self.getTimeDayRecord
            } 
             
             