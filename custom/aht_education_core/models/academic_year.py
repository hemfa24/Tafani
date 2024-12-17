
# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AcademicYear(models.Model):
    _name = 'aht.academic.year'
    _rec_name ='name'
    _description='Academic Year'
    _order='start_date DESC'

    name = fields.Char('Name',compute='get_session_name')
    start_date = fields.Date(sting='Start Date')
    end_date = fields.Date(sting='End Date')
    code  = fields.Char('Code')
    active= fields.Boolean(string='Active',default=True)

    @api.depends('start_date','end_date')
    def get_session_name(self):
        for record in self:
            if record.start_date and record.end_date:
                record.name=str(record.start_date.year)+'-'+ str(record.end_date.year)
            else:
                record.name=None