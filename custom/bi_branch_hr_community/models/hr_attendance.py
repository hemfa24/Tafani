# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import pycompat


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    branch_id = fields.Many2one('res.branch', string='Branch') 
    
    @api.model 
    def default_get(self, flds):
        """ Override to get default branch from employee """ 
        result = super(HrAttendance, self).default_get(flds)
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)

        if employee_id :
            if employee_id.branch_id:
                if 'branch_id' in flds:
                    result['branch_id'] = employee_id.branch_id
        return result