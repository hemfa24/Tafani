from odoo import api, fields, models, _
import base64
import io
from lxml import etree


class LecturerNotes(models.Model):
    _name = 'lecturer.notes'

    name = fields.Char(string="Name", required=True, states={'Confirm': [('readonly', True)]})
    academic_year = fields.Many2one('aht.academic.year', required=True, states={'Confirm': [('readonly', True)]})
    uploaded_by = fields.Many2one('res.users', string="Uploaded by", readonly="True",
                                  default=lambda self: self.env.user.id)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Confirm', 'Confirm'),
    ], string='State', default='Draft', )
    lecture_file = fields.Binary(string="File", attachment=True, states={'Confirm': [('readonly', True)]})
    file_name = fields.Char(string="File Name", required=True, states={'Confirm': [('readonly', True)]})
    attachment_id = fields.Many2one("ir.attachment", string="Attachment")
    course_offered = fields.Many2one('aht.course.offerings', string="Course", required=True,
                                     states={'Confirm': [('readonly', True)]})

    def createAttachment(self, rec):
        attachment = self.env['ir.attachment'].create({
            'name': rec.file_name,
            'datas': rec.lecture_file,
            'res_model': 'lecturer.notes',
            'res_id': rec.id,
            'type': 'binary',
        })
        return attachment

    @api.model_create_multi
    def create(self, vals_list):
        res = super(LecturerNotes, self).create(vals_list)
        attachment = self.createAttachment(res)
        res.write({'attachment_id': attachment.id})
        return res

    def write(self, vals):
        res = super(LecturerNotes, self).write(vals)
        if 'lecture_file' in vals:
            att_id = self.env['ir.attachment'].search([('name', '=', self.file_name)])
            if att_id:
                vals['attachment_id'] = att_id.id
                res = super(LecturerNotes, self).write(vals)
            else:
                attachment = self.createAttachment(self)
                vals['attachment_id'] = att_id.id
                res = super(LecturerNotes, self).write(vals)
        return res

    def downloadFile(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (self.attachment_id.id),
            'target': 'new',

        }

    def btn_confirm(self):
        self.write({'state': 'Confirm'})

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(LecturerNotes, self).get_view(view_id, view_type, **options)
        # if not self.env.user.has_group('aht_education_core.group_lecturer'):
        #     temp = etree.fromstring(result['arch'])
        #     temp.set('create', '0')
        #     temp.set('edit', '0')
        #     temp.set('delete', '0')
        #     result['arch'] = etree.tostring(temp)
        #

        return result
    # =======
#         result = super(LecturerNotes, self).get_view(view_id, view_type, **options)
#         if not self.env.user.has_group('aht_education_core.group_lecturer'):
#             temp = etree.fromstring(result['arch'])
#             temp.set('create', '0')
#             temp.set('edit', '0')
#             temp.set('delete', '0')
#             result['arch'] = etree.tostring(temp)
#
#         return result
# >>>>>>> saqib16.0
