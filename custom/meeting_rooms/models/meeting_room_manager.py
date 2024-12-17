from odoo import models, fields, api

class MeetingRoomManager(models.Model):
    _inherit = 'res.users'

    is_meeting_room_manager = fields.Boolean(string='Is Meeting Room Manager', default=False)

    @api.model
    def create(self, vals):
        user = super(MeetingRoomManager, self).create(vals)
        if vals.get('is_meeting_room_manager', False):
            user.groups_id = [(4, self.env.ref('base.group_system').id)]
        return user

    def write(self, vals):
        res = super(MeetingRoomManager, self).write(vals)
        if 'is_meeting_room_manager' in vals:
            for user in self:
                if vals.get('is_meeting_room_manager'):
                    user.groups_id = [(4, self.env.ref('base.group_system').id)]
                else:
                    user.groups_id = [(3, self.env.ref('base.group_system').id)]
        return res
