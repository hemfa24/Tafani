# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PrintProductLabelSection(models.Model):
    _name = "print.product.label.section"
    _description = 'Template Sections of Product Labels'
    _order = 'sequence'

    sequence = fields.Integer(default=100)
    template_id = fields.Many2one(
        comodel_name='print.product.label.template',
        string='Template',
        ondelete='cascade',
        required=True,
    )
    template_preview_html = fields.Html(related='template_id.preview_html')
    preview = fields.Boolean(default=True)
    type = fields.Selection(
        selection=[
            ('text', 'Text'),
            ('field', 'Model Field'),
        ],
        default='text',
        required=True,
    )
    value = fields.Char()
    value_format = fields.Char(string='Format')
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        ondelete='cascade',
        domain="[('id', 'in', field_ids)]",
    )
    field_name = fields.Char(related='field_id.name')
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Available Fields',
        help='Technical field for a domain',
        compute='_compute_field_ids',
    )
    field_ttype = fields.Selection(related='field_id.ttype')
    relation_model_id = fields.Many2one(
        comodel_name='ir.model',
        compute='_compute_relation_model_id',
    )
    relation_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        help='Field of the relation field, if you have selected '
             'the field with the type "many2one".',
    )
    height = fields.Float(
        string='Height, mm', digits=(10, 2), help='Section Height in mm.',
    )
    width = fields.Float(digits=(10, 2), help='Section Width.')
    width_measure = fields.Selection(
        selection=[
            ('%', 'Percents'),
            ('mm', 'mm'),
        ],
        default='%',
        required=True,
    )
    position = fields.Selection(
        selection=[
            ('none', 'Full Width'),
            ('left', 'Left Side'),
            ('right', 'Right Side'),
        ],
        string='Float',
        default='none',
        required=True,
    )
    line_height = fields.Float(
        digits=(10, 2), default=1.0, help='Section Line Height Ratio.',
    )
    align = fields.Selection(
        selection=[
            ('center', 'Center'),
            ('left', 'Left'),
            ('right', 'Right'),
            ('justify', 'Justify'),
        ],
        default='center',
        required=True,
    )
    font_size = fields.Float(digits=(10, 2), default=12, required=True)
    font_size_measure = fields.Selection(
        selection=[('px', 'Pixels'), ('mm', 'mm')],
        string='Measure',
        default='px',
        required=True,
    )
    font_weight = fields.Selection(
        selection=[
            ('100', '100'),
            ('normal', 'normal'),
            ('bold', 'bold'),
            ('900', '900'),
        ],
        default='normal',
        required=True,
    )
    letter_spacing = fields.Float(digits=(10, 2), help='Space between letters, in mm.')
    text_color = fields.Char(default='#000000')
    widget = fields.Selection(
        selection=[
            ('barcode', 'Barcode'),
            ('price', 'Price'),
        ],
    )
    padding_top = fields.Float(digits=(10, 2), help='Page Right Padding, in mm.')
    padding_bottom = fields.Float(digits=(10, 2), help='Page Bottom Padding, in mm.')
    padding_left = fields.Float(digits=(10, 2), help='Page Left Padding, in mm.')
    padding_right = fields.Float(digits=(10, 2), help='Page Right Padding, in mm.')
    with_border_top = fields.Boolean(string="Border Top")
    with_border_bottom = fields.Boolean(string="Border Bottom")
    with_border_left = fields.Boolean(string="Border Left")
    with_border_right = fields.Boolean(string="Border Right")
    border_width = fields.Integer(default=1, help='Border Width, in px')
    with_background = fields.Boolean(string="Background")
    background_color = fields.Char(default='#BBBBBB')
    active = fields.Boolean(default=True)

    @api.constrains('height')
    def _check_height(self):
        for section in self:
            if not section.height:
                raise ValidationError(_('The section height must be set.'))

    @api.depends('type')
    def _compute_field_ids(self):
        for section in self:
            if section.type == 'field':
                domain = [
                    ('model', '=', 'print.product.label.line')
                ] + self._get_field_domain()
                available_fields = self.env['ir.model.fields'].search(domain)
                section.field_ids = [(6, 0, available_fields.ids)]
            else:
                section.field_ids = None

    @api.depends('type', 'field_id')
    def _compute_relation_model_id(self):
        for section in self:
            if section.type == 'field' \
                    and section.field_id.ttype in self.relation_field_types():
                section.relation_model_id = self.env['ir.model'].search([
                    ('model', '=', section.field_id.relation)])[:1].id
            else:
                section.relation_model_id = None

    @api.model
    def text_field_types(self):
        return ['char', 'text', 'html']

    @api.model
    def digit_field_types(self):
        return ['float', 'monetary', 'integer']

    @api.model
    def relation_field_types(self):
        return ['many2one']

    @api.model
    def multi_relation_field_types(self):
        return ['many2many', 'one2many']

    @api.model
    def _get_field_domain(self):
        return [(
            'ttype',
            'in',
            self.text_field_types()
            + self.digit_field_types()
            + self.relation_field_types()
            # + self.multi_relation_field_types()
        )]

    @api.model
    def create(self, values):
        section = super(PrintProductLabelSection, self).create(values)
        template_sections = section.template_id.section_ids - section
        section['sequence'] = template_sections[-1].sequence + 1 \
            if template_sections else 100
        return section

    def get_float_position(self):
        self.ensure_one()
        width = 100 \
            if self.width_measure == '%' and self.width > 100 else self.width
        return "width: %(width).2f%(measure)s; float: %(float)s;" % {
            'width': width,
            'measure': self.width_measure,
            'float': self.position,
        }

    def get_border_style(self):
        self.ensure_one()
        border_style = ''
        for side in ['top', 'bottom', 'left', 'right']:
            if self['with_border_%s' % side]:
                border_style += 'border-%(side)s: %(width)dpx solid #000; ' % {
                    'side': side,
                    'width': self.border_width,
                }
        return border_style

    def get_background_style(self):
        self.ensure_one()
        bg_style = ''
        if self.with_background and self.background_color:
            bg_style += f'background-color: {self.background_color}; '
        return bg_style

    def get_html_style(self):
        self.ensure_one()
        style = "overflow: hidden; " \
                "height: %(height).2fmm; " \
                "padding: %(padding_top).2fmm %(padding_right).2fmm" \
                " %(padding_bottom).2fmm %(padding_left).2fmm; " \
                "text-align: %(align)s; " \
                "font-size: %(font_size)s; " \
                "color: %(text_color)s; " \
                "line-height: %(line_height).2f; " \
                "letter-spacing: %(letter_spacing).2fmm; " \
                "font-weight: %(font_weight)s;" % {
                    'height': self.height,
                    'align': self.align,
                    'font_size': '%.2f%s' % (self.font_size, self.font_size_measure),
                    'text_color': self.text_color,
                    'line_height': self.line_height,
                    'letter_spacing': self.letter_spacing,
                    'font_weight': self.font_weight,
                    'padding_top': self.padding_top,
                    'padding_right': self.padding_right,
                    'padding_bottom': self.padding_bottom,
                    'padding_left': self.padding_left,
                }
        # Section width settings
        style += "clear: both;" if self.position == 'none' else self.get_float_position()
        # Section borders
        style += self.get_border_style()
        # Section background
        style += self.get_background_style()
        return style

    def _get_related_field_value(self, record, field_name='name'):
        self.ensure_one()
        relation_field_name = \
            self.relation_field_id and self.relation_field_id.name or field_name
        return record[relation_field_name]

    def get_value(self, label):
        """Return value for a section depending on label.
        :param label: record of "print.product.label.line" model
        :return: str
        """
        self.ensure_one()
        section = self.sudo()
        value = ''

        if section.type == 'text':
            value = section.value or ''

        elif section.type == 'field':
            if section.field_id:
                field_name = section.field_id.name
                if section.field_id.ttype \
                        in self.text_field_types() + self.digit_field_types():
                    value = label[field_name]
                    
                elif section.field_id.ttype in self.relation_field_types():
                    record = label[field_name]
                    if record:
                        value = section._get_related_field_value(record)
        # Format value
        if value is False:
            value = ''
        if value and section.value_format:
            value = ('%s' % section.value_format) % value

        return value

    def name_get(self):
        return [(rec.id, "%s%s" % (
            rec.type == 'text' and rec.value
            or rec.type == 'field'
            and "%s %s" % (
                rec.field_id.field_description,
                rec.relation_field_id and rec.relation_field_id.field_description or '',
            ),
            rec.widget and (" (widget: %s)" % rec.widget) or '',
        )) for rec in self]
