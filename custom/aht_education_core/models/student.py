from odoo import api, fields, models, _
from lxml import etree

class Student(models.Model):
    _name = 'aht.student'
    _order = 'name ASC'
    _rec_name = 'complete_name'
    student_id = fields.Char(string='ID', required=True)
    first_name = fields.Char(string='First Name', required=True)
    middle_name = fields.Char(string='Middle Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    name = fields.Char(string='Name')
    birth_place = fields.Char(string='Birth Place')
    phone = fields.Char(string='Phone', required=True)
    address = fields.Char(string='Address')
    email = fields.Char(string='Email', required=True)
    nationality = fields.Many2one('res.country', required=True)
    marital_status = fields.Selection([('Single', 'single'), ('Married', 'married'), ('Widowed', 'widowed')],
                                      required=True)
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], required=True)
    blood_group = fields.Char(string='Blood Group')
    dob = fields.Date(string='DOB', required=True)
    image_1920 = fields.Image()
    user_id = fields.Many2one('res.users')

# =======
#     class_id = fields.Many2one('course.registration.class', string='Class', required=False)
# >>>>>>> 16.0

    user_created = fields.Boolean(default= False ,compute="isUserCreated")
    labgroup_id = fields.Many2one("lab.group",string ="Lab group" )

    state = fields.Selection([
        ('new', 'New'),
        ('enrolled', 'Enrolled'),
        ('pass_out', 'Pass Out'),
        ('drop_out', 'Drop Out')], string='State', default='new')


    complete_name =fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True ,precompute=True )
    department_id= fields.Many2one("aht.department" , string="Department")
    college_id = fields.Many2one("aht.college",string="College")
    class_id = fields.Many2one('course.registration.class', string='Class')
    academic_year = fields.Many2one('aht.academic.year',string="Current Term")


    @api.depends('first_name', 'middle_name','last_name')
    def _compute_complete_name(self):
        for nm in self:

            nm.complete_name = '%s %s %s'  % (nm.first_name,nm.middle_name,nm.last_name)


    @api.depends('user_id')
    def isUserCreated(self):
        for res in self:
            if res.user_id:
                res.user_created = True
            else:
                res.user_created = False


    def btn_create_user(self):
        if not self.user_id:
            record =  self.env['res.users'].sudo().create({
                    'login': self.first_name,
                    'email': self.email,
                    'name': self.first_name,
                    'image_1920': self.image_1920,

                })

            student_group_id = self.env.ref('aht_education_core.group_student')
            portal_group_id= self.env.ref('base.group_portal')
            internal_user_group= self.env.ref('base.group_user')

            internal_user_group.write({'users': [(3, record.id)]})
            portal_group_id.write({'users': [(4, record.id)]})
            student_group_id.write({'users': [(4, record.id)]})
            self.user_id= record.id
            print(f'record {record.id} created!')


    @api.depends('user_id.avatar_1920', 'image_1920')
    def _compute_avatar_1920(self):
        super()._compute_avatar_1920()

    @api.depends('user_id.avatar_1024', 'image_1024')
    def _compute_avatar_1024(self):
        super()._compute_avatar_1024()

    @api.depends('user_id.avatar_512', 'image_512')
    def _compute_avatar_512(self):
        super()._compute_avatar_512()

    @api.depends('user_id.avatar_256', 'image_256')
    def _compute_avatar_256(self):
        super()._compute_avatar_256()

    @api.depends('user_id.avatar_128', 'image_128')
    def _compute_avatar_128(self):
        super()._compute_avatar_128()

    def _compute_avatar(self, avatar_field, image_field):
        for employee in self:
            avatar = employee._origin[image_field]
            if not avatar:
                if employee.user_id:
                    avatar = employee.user_id[avatar_field]
                else:
                    avatar = employee._avatar_get_placeholder()
            employee[avatar_field] = avatar

    def btn_pass_out(self):
        self.write({'state': 'pass_out'})

    def btn_drop_out(self):
        self.write({'state': 'drop_out'})
    # @api.model
    # def get_view(self, view_id=None, view_type='form', **options):
    #     result = super(Student,self).get_view(view_id, view_type, **options) 
    #     if self.env.user.has_group('aht_education_core.group_student'):
    #         # rol_id = self.env.ref('aht_education_core.rule_student')
    #         # rol_id = self.env['ir.rule'].search([('id', '=', rol_id.id)])
    #         # group_id= self.env.ref('aht_education_core.group_student')
    #         #
    #         # rol_id.write({'groups': [(4    , group_id.id)]})
    #         temp = etree.fromstring(result['arch'])
    #         temp.set('create', '1')
    #         temp.set('edit', '1')
    #         temp.set('delete', '1')
    #         result['arch'] = etree.tostring(temp)

        # return result

        #