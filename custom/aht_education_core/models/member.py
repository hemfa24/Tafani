from odoo import models, api, fields, tools, _
from datetime import datetime, date
import qrcode
import base64
from io import BytesIO
from odoo.exceptions import UserError


class libMember(models.Model):
    _inherit = "res.partner"

    is_lib_member = fields.Boolean(string="is library member")
    membership_status = fields.Selection([('membership_expired', 'Membership Expired'),
                                          ('membership_not_expired', 'Membership Not Expired')],
                                         string='Membership status', compute="get_membersshipStatus")

    expires_on = fields.Date(string="Expires on")
    qr_code = fields.Binary("QR Code", compute='generate_qr_code')

    # late_member =  fields.Boolean(string="late_member")   
    member_id = fields.Char(string="Member id", readonly=True, copy=False)

    # issued_book_id = fields.Many2one("aht. sequence="5"book.issue", string="Issued Book id")
    # issued_book_ids =fields.One2many(comodel_name="book.issue",
    #     inverse_name='partner_id',
    #     string="Issued book line",
    #
    #     copy=True, auto_join=True)

    def generate_qr_code(self):
        for rec in self:
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )
                qr.add_data("Name : ")
                qr.add_data(rec.name)
                qr.add_data(", Member Id : ")
                qr.add_data(rec.member_id)

                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                rec.update({'qr_code': qr_image})

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        if not self.user_has_groups('aht_education_core.group_print_library_card'):
            for view in res['views'].values():
                view['toolbar'] = {'print': []}
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')):
                vals['member_id'] = self.env['ir.sequence'].next_by_code('res.partner')
        res = super(libMember, self).create(vals_list)
        return res

    @api.depends('expires_on')
    def get_membersshipStatus(self):
        for rec in self:

            if rec.expires_on:
                if rec.expires_on <= datetime.now().date():
                    rec.membership_status = 'membership_expired'
                else:
                    rec.membership_status = 'membership_not_expired'
            else:
                rec.membership_status = 'membership_not_expired'
