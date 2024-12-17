from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from datetime import datetime, date, timedelta

# from customaddons.aht_education_core.models import academic_year


class ClassRoom(models.Model):
    """Defining class room."""

    _name = "class.room"
    _description = "Class Room"

    name = fields.Char("Name", help="Class room name")
    number = fields.Char("Room Number", help="Class room number")

class ClassTimeTable(models.Model):

    """Defining model for time table."""

    _description = "Time Table"
    _name = "class.timetable"
    
    name = fields.Char(string="Name" )
    academic_year= fields.Many2one('aht.academic.year')
    class_id = fields.Many2one('course.registration.class', string='Class')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled')], string='State', default='draft')
    
    timetable_ids= fields.One2many("class.timetable.line", "timetable_id","TimeTable",
        help="Enter the timetable pattern")
    student_id = fields.Many2one('aht.student', string='Student', required=True ,states={'draft': [('readonly', False)] ,'confirm': [('readonly', True)], 'cancel': [('readonly', True)]},)
    
    
    def button_confirm(self):
        self.state = "confirm" 
        
    def button_cancel(self):
        self.state = "cancel"
        
        
    def button_reset(self):
        self.state = "draft"
        
        
class ClassTimeTableLine(models.Model):

    """Defining model for time table."""

    _description = "Time Table Line"
    _name = "class.timetable.line"
    
    week_day = fields.Selection(
        [
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        "Week day",
        help="Select weekday for timetable",
    )
    course_offered= fields.Many2one('aht.course.offerings' ,string='Course title')
    lecturer_id = fields.Many2one('hr.employee', string='Lecturer')
    class_room_id = fields.Many2one(
        "class.room",
        "Room",
        help="Class room in which tome table would be followed",
    )
    
    time_slot = fields.Many2one("time.slot",string="Time Slot")
    timetable_id = fields.Many2one("class.timetable",string="class time table")
    student_id = fields.Many2one("aht.student" , related= "timetable_id.student_id")
    
    
   
       