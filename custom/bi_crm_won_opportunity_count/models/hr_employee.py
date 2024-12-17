# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    won_opportunity = fields.Integer(string="Won Opportunity")
    amount = fields.Integer(string="Amount")
    is_selected = fields.Boolean(string="fields to view",compute="_compute_is_selected")

    
    def _compute_is_selected(self):
        self.is_selected = False
        res_config_settings_obj = self.env['res.config.settings']
        default_values = res_config_settings_obj.default_get(list(res_config_settings_obj.fields_get()))
        vals = default_values.get('opportunity_count')

        if vals:
            self.is_selected = True
            crm_lead_obj = self.env['crm.lead'].search([('stage_id.is_won', '=', True)])

            employee_record_list = []
            for record in crm_lead_obj:
                hr_employee_obj = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)])
                if hr_employee_obj not in employee_record_list:
                    employee_record_list.append(hr_employee_obj)
            if not employee_record_list:
                for record in self:
                    record.write({'won_opportunity': 0,
                               'amount': 0})
            hr_employee_id = self.env['hr.employee'].search([])
            for emp in hr_employee_id:
                if emp not in employee_record_list:
                    emp.write({'won_opportunity': 0,
                                  'amount': 0})

            for rec in employee_record_list:
                count = 0
                total = 0
                crm_opportunities = self.env['crm.lead'].search(
                    [('user_id', '=', rec.user_id.id), ('stage_id.is_won', '=', True)])
                opportunity_count = len(crm_opportunities)

                for count in crm_opportunities:
                    total += count.expected_revenue

                rec.write({'won_opportunity': opportunity_count,
                            'amount': total})