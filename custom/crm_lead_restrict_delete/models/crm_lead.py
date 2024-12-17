# Copyright 2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, api

class CrmLead(models.Model):
    _inherit = "crm.lead"


    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        key = super()._get_view_cache_key(view_id=view_id, view_type=view_type, options=options)
        return key + (self.env.user.has_group('crm_lead_restrict_delete.crm_lead_delete_group'),)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super(CrmLead,self)._get_view(view_id, view_type, **options)
        if view_type == 'form' and self.env.user.has_group('crm_lead_restrict_delete.crm_lead_delete_group'):
            for node in arch.xpath("//form"):
                node.set('delete', '1')
        if view_type == 'tree' and self.env.user.has_group('crm_lead_restrict_delete.crm_lead_delete_group'):
            for node in arch.xpath("//tree"):
                node.set('delete','1')

        return arch, view
