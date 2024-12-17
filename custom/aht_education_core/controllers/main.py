# -*- coding: utf-8 -*-
import base64
import json
import os
from collections import defaultdict
from odoo import http, fields
from odoo.http import request
from .secuirty import StudentAuthentication
from odoo.addons.web.controllers.main import Binary


class HomePage(http.Controller):

    @http.route(['/'], type='http', auth="public", website=True)
    def home_page(self):
        if request.env.user.id and request.env.user.has_group('base.group_user'):
            return request.redirect('/web')
        elif request.env.user.id and request.env.user.has_group('base.group_portal'):
            return request.redirect('/student_portal')
        else:
            return request.redirect('/web/login')


class StudentWebTemplates(http.Controller):
    @http.route('/web/login_successful', auth='public', website=True)
    def web_login(self, **kw):
        return request.redirect('/')

    @http.route('/lecture_notes', auth='public', website=True)
    def lecture_notes(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})

        student = auth['student']
        registration = request.env['course.registration.student'].sudo().search(
            [('student_id', '=', student.id), ('state', '=', 'approved')])
        courses = registration.course_ids
        student = auth['student']
        return request.render('aht_education_core.lecture_notes', {
            'student': student,
            'courses': courses,
        })

    @http.route('/custom/download_attachment/<int:attachment_id>', type='http', auth='user')
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if attachment:
            file_content = base64.b64decode(attachment.datas)
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', 'attachment; filename=%s' % attachment.name),
            ]
            return request.make_response(file_content, headers=headers)
        else:
            return request.not_found()

    @http.route('/getCourseContent/<int:course_id>', type='http', auth='user', website=True)
    def getCourseContent(self, course_id, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
        try:
            data = []
            notes = request.env['lecturer.notes'].sudo().search(
                [('course_offered.id', '=', course_id), ('state', '=', 'Confirm')])
            sno = 0
            for note in notes:
                sno += 1
                _, file_extension = os.path.splitext(note.file_name)
                data.append({
                    'sno': sno,
                    'attachment_id': note.attachment_id.id,
                    'title': note.name,
                    'uploaded_by': note.uploaded_by.name,
                    'document_type': file_extension[1:],
                })
            return json.dumps({
                'error': 0,
                'courses': data
            })
        except Exception as e:
            return json.dumps({'error': 1, 'message': str(e)})

    @http.route(['/action_redirect_download_solution/<int:submission_id>/<int:download>/<string:name>',
                 '/action_redirect_download_solution/<int:submission_id>'], type='http', auth='user', website=True)
    def action_redirect_download_solution(self, submission_id, download=0, name=None):
        try:
            auth = StudentAuthentication.system_auth(self, submission_id=submission_id)
            if auth['unauthorized']:
                raise

            record = Binary.content_common(self, model='aht.assignment.submission', id=submission_id,
                                           field='solution_file',
                                           filename=None)
            if record.status_code in [200, 304]:
                assessment = request.env['aht.assignment.submission'].sudo().browse(submission_id)
                file_name = assessment.file_name
                if file_name:
                    parts = file_name.split('.')
                    if len(parts) > 1:
                        Filename = ".".join(parts[:-1])
                        extension = parts[-1]
                return (
                    record if download else json.dumps({'error': 0, 'name': Filename + extension}))
            return json.dumps({
                'error': 1,
                'message': "not found",
            })
        except:
            return json.dumps({
                'error': 1,
                'message': "not authorized",
            })

    @http.route(['/action_redirect_download_uploaded/<int:submission_id>/<int:download>/<string:name>',
                 '/action_redirect_download_uploaded/<int:submission_id>'], type='http', auth='user', website=True)
    def action_redirect_download_uploaded(self, submission_id, download=0, name=None):
        try:
            auth = StudentAuthentication.system_auth(self, submission_id=submission_id)
            if auth['unauthorized']:
                raise
            record = Binary.content_common(self, model='aht.assignment.submission', id=submission_id,
                                           field='answer_file',
                                           filename=None)
            if record.status_code in [200, 304]:
                submission = request.env['aht.assignment.submission'].sudo().browse(submission_id)
                file_name = submission.file_name
                if file_name:
                    parts = file_name.split('.')
                    if len(parts) > 1:
                        Filename = ".".join(parts[:-1])
                        extension = parts[-1]
                return (record if download else json.dumps({'error': 0, 'name': Filename + extension}))
            return json.dumps({
                'error': 1,
                'message': "not found",
            })
        except:
            return json.dumps({
                'error': 1,
                'message': "not authorized",
            })

    # @http.route('/custom/download_question_file/<int:attachment_id>', type='http', auth='user')
    # def download_attachment(self, attachment_id):
    #     attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
    #     if attachment:
    #         file_content = base64.b64decode(attachment.datas)
    #         headers = [
    #             ('Content-Type', 'application/octet-stream'),
    #             ('Content-Disposition', 'attachment; filename=%s' % attachment.name),
    #         ]
    #         return request.make_response(file_content, headers=headers)
    #     else:
    #         return request.not_found()
    #
    # @http.route('/download_question_file/<int:submission_id>', type='http', auth='user')
    # def download_question_file(self, submission_id):
    #     auth = StudentAuthentication.system_auth(self)
    #     if auth['unauthorized']:
    #         return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
    #
    #     try:
    #         submission = request.env['aht.assignment.submission'].sudo().browse(submission_id)
    #         if submission:
    #             attachment_id = submission.attachment_id_question.id
    #             return json.dumps({
    #                 'message': 'Success',
    #                 'attachment_id': attachment_id
    #             })
    #     except Exception as e:
    #         return json.dumps({
    #             'error': 1,
    #             'message': str(e),
    #         })

    @http.route(['/action_redirect_download_assessment/<int:submission_id>/<int:download>/<string:name>',
                 '/action_redirect_download_assessment/<int:submission_id>'], type='http', auth='user', website=True)
    def action_redirect_download_assessment(self, submission_id, download=0, name=None):
        try:
            auth = StudentAuthentication.system_auth(self, submission_id=submission_id)
            if auth['unauthorized']:
                raise
            record = Binary.content_common(self, model='aht.assignment.submission', id=submission_id,
                                           field='question_file',
                                           filename=None)
            if record.status_code in [200, 304]:
                submission = request.env['aht.assignment.submission'].sudo().browse(submission_id)
                file_name = submission.file_name
                if file_name:
                    parts = file_name.split('.')
                    if len(parts) > 1:
                        Filename = ".".join(parts[:-1])  # Join all parts except the last one
                        extension = parts[-1]  # The last part is the extension
                return (record if download else json.dumps({'error': 0, 'name': Filename + extension}))
            return json.dumps({
                'error': 1,
                'message': "not found",
            })
        except:
            return json.dumps({
                'error': 1,
                'message': "not authorized",
            })

    @http.route('/delete_assignment_file', auth="user", website=True, methods=['POST'], csrf=False)
    def delete_assignment_file(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return json.dumps({
                'error': 1,
                'message': "not authorized",
            })
        try:
            submission_id = request.httprequest.form.get('submission_id')
            submission = request.env['aht.assignment.submission'].sudo().browse(int(submission_id))
            if submission:
                submission.write({
                    'answer_file': False,
                    'state': 'Draft'
                })
                return json.dumps({
                    'error': 0,
                    'message': "success"
                })

        except Exception as e:
            return json.dumps({
                'error': 1,
                'message': str(e),
            })

    @http.route('/store_assignment_file', auth="user", website=True, methods=['POST'], csrf=False)
    def store_assignment_file(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return json.dumps({
                'error': 1,
                'message': "not authorized",
            })
        try:
            submission_id = request.httprequest.form.get('submission_id')
            submission = request.env['aht.assignment.submission'].sudo().browse(int(submission_id))
            attachment_data = request.httprequest.files.get('file')
            if attachment_data:
                attachment_binary = base64.b64encode(attachment_data.read())
            else:
                attachment_binary = None
            submission.write({
                'answer_file': attachment_binary,
                'state': 'Submitted'
            })
            return json.dumps({
                'error': 0,
                'message': "success"
            })
        except Exception as e:
            return json.dumps({
                'error': 1,
                'message': str(e),
            })

    @http.route('/attendance_details/<int:course_id>', type='http', auth='user')
    def attendanceDetails(self, course_id):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
        student = auth['student']
        attendances = request.env['student.course.attendance'].sudo().search(
            [('course_offered.id', '=', course_id), ('attendance_lines.student', '=', student.id)])
        return request.render('aht_education_core.student_attendance_details', {
            'attendances': attendances,
        })

    @http.route('/attendance', auth='public', website=True)
    def student_attendance(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})

        student = auth['student']
        course_reg_lines = request.env['course.registration.lines'].sudo().search(
            [('registration.student_id', '=', student.id)])
        student_attendance = request.env['student.course.attendance'].sudo().search(
            [('attendance_lines.student', '=', student.id),
             ('course_offered.id', 'in', course_reg_lines.course_offered.ids),
             ('state', '=', 'Submitted')])
        attendance_dict = defaultdict(
            lambda: {'total_hours': 0, 'present_hours': 0, 'absent_hours': 0,
                     'credit_hours': 0, 'faculty': '', 'class_type': '', 'course_offered_id': 0})

        for attendance_line in student_attendance:
            course_name = attendance_line.course_offered.course_name.name.name
            class_hours = attendance_line.class_hours
            status = attendance_line.attendance_lines.status
            faculty = attendance_line.course_offered.faculty.name
            credit_hours = attendance_line.course_offered.credit_hours
            course_offered_id = attendance_line.course_offered.id
            attendance_dict[course_name]['total_hours'] += int(class_hours)
            if status != 'Absent':
                attendance_dict[course_name]['present_hours'] += int(status)
            attendance_dict[course_name]['absent_hours'] = attendance_dict[course_name]['total_hours'] - \
                                                           attendance_dict[course_name]['present_hours']
            attendance_dict[course_name]['credit_hours'] = int(credit_hours)
            attendance_dict[course_name]['faculty'] = faculty
            attendance_dict[course_name]['course_offered_id'] = course_offered_id

        return request.render('aht_education_core.student_attendance', {
            'student': student,
            'attendance': attendance_dict,
        })

    @http.route('/timetable', auth='public', website=True)
    def student_timetable(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
        student = auth['student']
        timetable_lines =[] 
        student_academic_year = student.academic_year
        if student_academic_year:
            timetable_recs= request.env['class.timetable'].sudo().search([('academic_year','=',student_academic_year.id),
                                                                         ('student_id','=',student.id),
                                                                         ('state','=','confirm')])
            
            if timetable_recs:
                timetable_lines= timetable_recs.timetable_ids
                
        return request.render('aht_education_core.student_timetable', {
            'student': student,
            'timetable_lines': timetable_lines,
        })

    @http.route('/assignments', auth='public', website=True)
    def assignments(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
        student = auth['student']
        registration = request.env['course.registration.student'].sudo().search(
            [('student_id', '=', student.id), ('state', '=', 'approved')])
        courses = registration.course_ids
        assessment_submissions = request.env['aht.assignment.submission'].sudo().search(
            [('student', '=', student.id)])
        return request.render('aht_education_core.assignment_submission', {
            'student': student,
            'courses': courses,
            'assessment_submissions': assessment_submissions,

        })

    @http.route('/student_portal', auth='public', website=True)
    def student_portal(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})

        student = auth['student']
        return request.render('aht_education_core.student_portal', {
            'student': student
        })
   
   
   
   
    @http.route('/student_profile', auth='public', website=True)
    def student_profile(self, **kw):
        auth = StudentAuthentication.system_auth(self)
        if auth['unauthorized']:
            return request.render('aht_education_core.unauthorized', {'current_user': auth['user']})
        student = auth['student']
        return request.render('aht_education_core.student_profile', {
            'student': student
        })