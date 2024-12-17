# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class College(models.Model):
    _name = 'aht.college'
    _rec_name = 'name'
    _description='module for college'

    name = fields.Char(string='Name')
    code = fields.Char('Code')
    title_image= fields.Binary(string="image" ,attachment=True)
    abbreviation= fields.Char('Abbreviation')
    about_college_english= fields.Html(string='About College')
    dean_message_english= fields.Html(string='Dean Message')
    mission_english = fields.Html(string='Mission')
    vision_english = fields.Html(string='Goals')
    college_contact= fields.Html(string='Contact')
    facebook_link= fields.Char(string='Facebook')
    college_email = fields.Char(string='College Email')
    _sql_constraints = [
        ('unique_name',
         'unique(name)', 'Name should be unique as per college!'), ('unique_code',
         'unique(code)', 'Code should be unique as per college!')]
