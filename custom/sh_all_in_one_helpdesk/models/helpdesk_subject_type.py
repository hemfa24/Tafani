# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class HelpdeskSubjectType(models.Model):
    _name = 'helpdesk.sub.type'
    _description = 'Helpdesk Subject Type'
    _rec_name = 'name'

    name = fields.Char('Subject name', required=True, translate=True)
    ticket_type_id = fields.Many2one('sh.helpdesk.ticket.type', string='Ticket type')
