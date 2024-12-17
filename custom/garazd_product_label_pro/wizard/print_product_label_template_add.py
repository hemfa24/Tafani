from odoo import fields, models
from odoo.addons.base.models.report_paperformat import PAPER_SIZES


class PrintProductLabelTemplateAdd(models.TransientModel):
    _name = "print.product.label.template.add"
    _description = 'Wizard to add a new product label templates'

    width = fields.Integer(help='Label Width in mm.', required=True)
    height = fields.Integer(help='Label Height in mm.', required=True)
    rows = fields.Integer(default=1, required=True)
    cols = fields.Integer(default=1, required=True)
    paper_format = fields.Selection(
        selection=[
            ('custom', 'Custom'),
            ('A4', 'A4'),
            ('Letter', 'US Letter'),
        ],
        help="Select Proper Paper size",
        default='custom',
        required=True,
    )
    orientation = fields.Selection(
        selection=[
            ('Portrait', 'Portrait'),
            ('Landscape', 'Landscape'),
        ],
        default='Portrait',
        required=True,
    )
    margin_top = fields.Float(digits=(10, 2), help='Page Top Margin in mm.')
    margin_bottom = fields.Float(digits=(10, 2), help='Page Bottom Margin in mm.')
    margin_left = fields.Float(digits=(10, 2), help='Page Left Margin in mm.')
    margin_right = fields.Float(digits=(10, 2), help='Page Right Margin in mm.')

    def _get_label_name(self):
        self.ensure_one()
        return 'Label: %s' % '%s%s' % (
            "%s " % self.paper_format if self.paper_format != 'custom' else '',
            "%dx%d mm" % (self.width, self.height),
        )

    def _create_paperformat(self):
        self.ensure_one()
        return self.env['report.paperformat'].sudo().create({
            'name': self._get_label_name(),
            'format': self.paper_format,
            'page_width': 0 if self.paper_format != 'custom' else self.width,
            'page_height': 0 if self.paper_format != 'custom' else self.height,
            'orientation': self.orientation,
            'margin_top': self.margin_top,
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'margin_right': self.margin_right,
            'header_spacing': 0,
            'header_line': False,
            'disable_shrinking': True,
            'dpi': 96,
            'default': False,
        })

    def action_create(self):
        self.ensure_one()
        template = self.env['print.product.label.template'].create({
            'name': self._get_label_name().replace(':', ''),
            'paperformat_id': self._create_paperformat().id,
            'width': self.width,
            'height': self.height,
            'rows': 1 if self.paper_format == 'custom' else self.rows,
            'cols': 1 if self.paper_format == 'custom' else self.cols,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': template._name,
            'res_id': template.id,
            'view_mode': 'form',
        }
