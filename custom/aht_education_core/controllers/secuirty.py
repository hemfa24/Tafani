# -*- coding: utf-8 -*-
import json
from odoo.http import request, route, Controller
import base64


class StudentAuthentication(Controller):
    #
    #  each request.env should be with sudo() and
    #  each domain must have a condition with
    #   user or student
    #  ('user_id', '=', user.id) / ('student', '=', student.id)
    #
    def system_auth(self, submission_id=0):
        unauthorized = 0
        user = request.env.user
        student = request.env['aht.student'].sudo().search([('user_id', '=', user.id)])

        if not user.id or not student.id:
            unauthorized = 1

        values = {
            'user': user,
            'student': student,
            'unauthorized': unauthorized
        }

        if submission_id:
            submission = request.env['aht.assignment.submission'].sudo().browse(submission_id)
            if not submission:
                values['unauthorized'] = 1
        return values
