# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PrintProductLabelTemplate(models.Model):
    _name = "print.product.label.template"
    _description = 'Templates of Product Labels'
    _order = 'sequence'

    sequence = fields.Integer(default=100)
    name = fields.Char(required=True)
    section_ids = fields.One2many(
        comodel_name='print.product.label.section',
        inverse_name='template_id',
        string='Sections',
    )
    section_count = fields.Integer(compute='_compute_section_count')
    paperformat_id = fields.Many2one(
        comodel_name='report.paperformat',
        # All label paperformats should have prefix "Label: "
        domain="[('name', 'like', 'Label: %')]",
        readonly=True,
        required=True,
    )
    format = fields.Selection(related='paperformat_id.format', store=True)
    orientation = fields.Selection(
        related='paperformat_id.orientation',
        readonly=False,
        required=True,
        help='Page Orientation. Only system administrators can change this value.',
    )
    rows = fields.Integer(default=1, required=True)
    cols = fields.Integer(default=1, required=True)
    margin_top = fields.Float(
        related='paperformat_id.margin_top',
        help='Page Top Margin in mm. Only system administrators can change this value.',
        readonly=False,
    )
    margin_bottom = fields.Float(
        related='paperformat_id.margin_bottom',
        help='Page Bottom Margin in mm. '
             'Only system administrators can change this value.',
        readonly=False,
    )
    margin_left = fields.Float(
        related='paperformat_id.margin_left',
        help='Page Left Margin in mm. Only system administrators can change this value.',
        readonly=False,
    )
    margin_right = fields.Float(
        related='paperformat_id.margin_right',
        help='Page Right Margin in mm. '
             'Only system administrators can change this value.',
        readonly=False,
    )
    padding_top = fields.Float(
        default=0, digits=(10, 2), help='Label Right Padding in mm.')
    padding_bottom = fields.Float(
        default=0, digits=(10, 2), help='Label Bottom Padding in mm.')
    padding_left = fields.Float(
        default=0, digits=(10, 2), help='Label Left Padding in mm.')
    padding_right = fields.Float(
        default=0, digits=(10, 2), help='Label Right Padding in mm.')
    label_style = fields.Char(string='Custom Label Style')
    width = fields.Float(digits=(10, 2), help='Label Width in mm.')
    height = fields.Float(digits=(10, 2), help='Label Height in mm.')
    row_gap = fields.Float(
        string='Horizontal',
        digits=(10, 2),
        default=0,
        help='Horizontal gap between labels, in mm.',
    )
    col_gap = fields.Float(
        string='Vertical',
        digits=(10, 2),
        default=0,
        help='Vertical gap between labels, in mm.',
    )
    is_oversized = fields.Boolean(compute='_compute_is_oversized')
    description = fields.Char()
    demo_product_id = fields.Many2one(
        comodel_name='product.product',
        default=lambda self: self.env['product.product'].search([
            ('barcode', '!=', False)
        ], limit=1),
    )
    preview = fields.Boolean(default=True)
    preview_html = fields.Html(compute='_compute_preview_html')
    active = fields.Boolean(default=True)

    @api.depends('section_ids')
    def _compute_section_count(self):
        for template in self:
            template.section_count = len(template.section_ids)

    @api.depends('width', 'height', 'section_ids', 'section_ids.height')
    def _compute_is_oversized(self):
        for template in self:
            total_height = sum(template.section_ids.mapped('height')) \
                + template.padding_top + template.padding_bottom
            template.is_oversized = template.height < total_height

    def _set_paperformat(self):
        self.ensure_one()
        self.env.ref(
            'garazd_product_label.action_report_product_label_from_template'
        ).sudo().paperformat_id = self.paperformat_id.id

    def write(self, vals):
        """If the Dymo label width or height were changed,
        we should change it to the related paperformat."""
        res = super(PrintProductLabelTemplate, self).write(vals)
        for template in self:
            if template.paperformat_id.format == 'custom':
                template.paperformat_id.sudo().write({
                    'page_width': template.width,
                    'page_height': template.height,
                })
        return res

    def unlink(self):
        paperformats = self.mapped('paperformat_id')
        res = super(PrintProductLabelTemplate, self).unlink()
        paperformats.sudo().unlink()
        return res

    def get_demo_product_label(self):
        self.ensure_one()
        if not self.demo_product_id:
            raise UserError(_("Please select a demo product."))
        return self.env['print.product.label.line'].create({
            'product_id': self.demo_product_id.id,
            'price': self.demo_product_id.lst_price,
            'barcode': self.demo_product_id.barcode,
        })

    @api.depends('preview', 'demo_product_id')
    def _compute_preview_html(self):
        for template in self:
            template.preview_html = \
                template.demo_product_id and template.get_preview_html() or ''

    def get_preview_html(self):
        self.ensure_one()
        label = self.get_demo_product_label()
        sections = ''
        for section in self.section_ids:
            sections += f"""
                <div style="{section.get_html_style()}">
                    { section.widget == 'barcode' and label.barcode and
                      '<img src="/report/barcode/EAN13/{}?quiet=0" style="width:85%;height:100%;"/>'.format(label.barcode)
                      or section.widget == 'price' and 
                      '<div>{}&nbsp;<span style="line-height: 1.5;" class="oe_currency_value">{:.0f}.</span><span class="oe_currency_value" style="font-size:0.5em; line-height: 1.5;">00</span></div>'.format(label.currency_id.symbol, label.price)  
                      or '<div style="white-space:normal">{}</div>'.format(section.get_value(label))
                    }
                </div>
            """
        return f"""
        <div style="background-color: #CCCCCC; width: 100%; height: 100%; padding: 15px; overflow: hidden;">
        <div style="width: {self.width}mm; height: {self.height}mm; background-color: #FFFFFF; margin: auto; padding: {self.padding_top}mm {self.padding_right}mm {self.padding_bottom}mm {self.padding_left}mm;">
            <div name="transform_div">
            {sections}
            </div>
        </div>
        </div>
        """
