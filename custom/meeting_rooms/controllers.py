from odoo import http
from odoo.http import request

class MeetingRoomController(http.Controller):
    @http.route('/meeting/accept/<int:booking_id>/<int:attendee_id>', type='http', auth="public", website=True)
    def accept_meeting(self, booking_id, attendee_id, **kwargs):
        attendee = request.env['meeting.attendee.response'].browse(attendee_id)
        if attendee:
            attendee.status = 'accepted'
        return request.render('meeting_rooms.accept_template', {'user': attendee.attendee_id, 'booking': attendee.booking_id})

    @http.route('/meeting/decline/<int:booking_id>/<int:attendee_id>', type='http', auth="public", website=True)
    def decline_meeting(self, booking_id, attendee_id, **kwargs):
        attendee = request.env['meeting.attendee.response'].browse(attendee_id)
        if attendee:
            attendee.status = 'declined'
        return request.render('meeting_rooms.decline_template', {'user': attendee.attendee_id, 'booking': attendee.booking_id})
