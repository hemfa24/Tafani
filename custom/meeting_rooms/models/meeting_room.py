from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class MeetingRoom(models.Model):
    _name = 'meeting.room'
    _description = 'Meeting Room'
    _inherit = ['mail.thread']

    name = fields.Char(string='Room Name', required=True, track_visibility='onchange')
    location = fields.Char(string='Location', track_visibility='onchange')
    capacity = fields.Integer(string='Capacity', track_visibility='onchange')
    amenities = fields.Text(string='Amenities', track_visibility='onchange')
    background_color_available = fields.Char(string='Available Background Color', default='#00FF00', track_visibility='onchange')
    background_color_booked = fields.Char(string='Booked Background Color', default='#FF0000', track_visibility='onchange')
    is_available = fields.Boolean(string='Is Available', compute='_compute_is_available', track_visibility='onchange')
    next_booking_start = fields.Datetime(string='Next Booking Start', compute='_compute_next_booking_start', track_visibility='onchange')
    max_duration = fields.Integer(string='Maximum Booking Duration (hours)', default=4, track_visibility='onchange')
    buffer_time = fields.Integer(string='Buffer Time Between Bookings (minutes)', default=30, track_visibility='onchange')

    _sql_constraints = [
        ('meeting_room_name_uniq', 'unique (name)', 'The meeting room name must be unique!')
    ]

    @api.depends('name')
    def _compute_is_available(self):
        for room in self:
            current_time = fields.Datetime.now()
            overlapping_bookings = self.env['meeting.booking'].search([
                ('room_id', '=', room.id),
                ('start_time', '<=', current_time),
                ('end_time', '>=', current_time),
            ])
            room.is_available = not overlapping_bookings

    @api.depends('name')
    def _compute_next_booking_start(self):
        for room in self:
            current_time = fields.Datetime.now()
            next_booking = self.env['meeting.booking'].search([
                ('room_id', '=', room.id),
                ('start_time', '>=', current_time),
            ], order='start_time', limit=1)
            room.next_booking_start = next_booking.start_time if next_booking else False

class Booking(models.Model):
    _name = 'meeting.booking'
    _description = 'Meeting Booking'
    _inherit = ['mail.thread']

    name = fields.Char(string='Meeting Name', required=True, track_visibility='onchange')
    meeting_type = fields.Selection([
        ('staff_meeting', 'Staff Meeting'),
        ('training', 'Training'),
        ('client', 'Client'),
        ('workshop', 'Workshop'),
        ('general_meeting', 'General Meeting')
    ], string='Meeting Type', required=True, track_visibility='onchange')
    room_id = fields.Many2one('meeting.room', string='Meeting Room', required=True, track_visibility='onchange')
    organizer_id = fields.Many2one('res.users', string='Organizer', default=lambda self: self.env.user, required=True, track_visibility='onchange')
    start_time = fields.Datetime(string='Start Time', required=True, track_visibility='onchange')
    end_time = fields.Datetime(string='End Time', required=True, track_visibility='onchange')
    duration = fields.Float(string='Duration', compute='_compute_duration', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Booked By', default=lambda self: self.env.user, track_visibility='onchange')
    attendees = fields.Many2many('res.users', string='Attendees', track_visibility='onchange')
    attendee_response_ids = fields.One2many('meeting.attendee.response', 'booking_id', string='Attendee Responses')
    recurrence_interval = fields.Integer(string='Recurrence Interval', default=1, track_visibility='onchange')
    is_recurring = fields.Boolean(string='Is Recurring', track_visibility='onchange')
    recurrence_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], string='Recurrence Type', track_visibility='onchange')
    recurrence_end_date = fields.Date(string='Recurrence End Date', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft', string='Status', track_visibility='onchange')

    _sql_constraints = [
        ('meeting_booking_unique', 'unique (room_id, start_time, end_time)', 'The room is already booked for the specified time!')
    ]

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for booking in self:
            if booking.start_time and booking.end_time:
                duration = (booking.end_time - booking.start_time).total_seconds() / 3600
                booking.duration = duration

    @api.constrains('start_time', 'end_time')
    def _check_booking_times(self):
        for booking in self:
            if booking.start_time >= booking.end_time:
                raise ValidationError('End time must be after start time.')
            overlapping_bookings = self.env['meeting.booking'].search([
                ('room_id', '=', booking.room_id.id),
                ('id', '!=', booking.id),
                ('start_time', '<', booking.end_time),
                ('end_time', '>', booking.start_time),
            ])
            if overlapping_bookings:
                raise ValidationError('The meeting room is already booked for the selected time.')

    @api.model
    def create(self, vals):
        room = self.env['meeting.room'].browse(vals['room_id'])
        start_time = fields.Datetime.from_string(vals['start_time'])
        end_time = fields.Datetime.from_string(vals['end_time'])
        buffer_start = start_time - timedelta(minutes=room.buffer_time)
        buffer_end = end_time + timedelta(minutes=room.buffer_time)
        overlapping_bookings = self.search([
            ('room_id', '=', room.id),
            ('start_time', '<', buffer_end),
            ('end_time', '>', buffer_start),
        ])
        if overlapping_bookings:
            raise ValidationError('The meeting room is already booked for the selected time including buffer time.')
        booking = super(Booking, self).create(vals)
        if 'is_recurring' in vals and vals['is_recurring']:
            self._create_recurrences(booking)
        
        return booking

    def action_confirm(self):
        self.state = 'confirmed'
        # Send email notification to organizer and attendees
        self._send_booking_confirmation(self)

    def _create_recurrences(self, booking):
        start_date = fields.Datetime.from_string(booking.start_time)
        end_date = fields.Datetime.from_string(booking.recurrence_end_date)
        
        if booking.recurrence_type == 'daily':
            interval = timedelta(days=booking.recurrence_interval)
        elif booking.recurrence_type == 'weekly':
            interval = timedelta(weeks=booking.recurrence_interval)
        elif booking.recurrence_type == 'monthly':
            interval = relativedelta(months=booking.recurrence_interval)
        while start_date + interval <= end_date:
            start_date += interval
            end_time = start_date + (fields.Datetime.from_string(booking.end_time) - fields.Datetime.from_string(booking.start_time))
            self.create({
                'name': booking.name,
                'meeting_type': booking.meeting_type,
                'room_id': booking.room_id.id,
                'start_time': start_date,
                'end_time': end_time,
                'organizer_id': booking.organizer_id.id,
                'attendees': [(6, 0, booking.attendees.ids)],
                'user_id': booking.user_id.id,
                'state': 'draft',
            })

    def write(self, vals):
        if not self.env.user.has_group('base.group_system') and not self.env.user.is_meeting_room_manager:
            if any(booking.user_id != self.env.user for booking in self):
                raise AccessError("You can only edit your own bookings.")
        result = super(Booking, self).write(vals)
        
        return result

    def unlink(self):
        if not self.env.user.has_group('base.group_system') and not self.env.user.is_meeting_room_manager:
            if any(booking.user_id != self.env.user for booking in self):
                raise AccessError("You can only delete your own bookings.")
        
        return super(Booking, self).unlink()

    @api.model
    def send_booking_reminders(self):
        now = fields.Datetime.now()
        upcoming_bookings = self.search([('start_time', '<=', now + timedelta(hours=24)), ('start_time', '>', now)])
        for booking in upcoming_bookings:
            template = self.env.ref('meeting_rooms.email_template_booking_reminder')
            self.env['mail.template'].browse(template.id).send_mail(booking.id, force_send=True)

    def _send_booking_confirmation(self, booking):
        template = self.env.ref('meeting_rooms.email_template_booking_confirmation')
        email_to = booking.organizer_id.email
        email_cc = ','.join(booking.attendees.mapped('email'))
        self.env['mail.template'].browse(template.id).send_mail(booking.id, email_values={'email_to': email_to, 'email_cc': email_cc}, force_send=True)

    def get_accept_url(self):
        return '/meeting/accept/%d/%d' % (self.id, request.env.user.id)

    def get_decline_url(self):
        return '/meeting/decline/%d/%d' % (self.id, request.env.user.id)

class AttendeeResponse(models.Model):
    _name = 'meeting.attendee.response'
    _description = 'Attendee Response'

    booking_id = fields.Many2one('meeting.booking', string='Booking', required=True, ondelete='cascade')
    attendee_id = fields.Many2one('res.users', string='Attendee', required=True, ondelete='cascade')
    status = fields.Selection([('accepted', 'Accepted'), ('declined', 'Declined')], string='Status', required=True)
