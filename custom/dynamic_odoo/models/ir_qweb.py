import ast
from lxml import etree
from odoo.tools.json import scriptsafe
from textwrap import dedent

# from odoo.addons.base.models.qweb import QWeb
from odoo import models, api
from odoo.addons.base.models.ir_qweb import indent_code
from markupsafe import Markup, escape


class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _render(self, template, values=None, **options):
        if values is None:
            values = {}
        values['json'] = scriptsafe
        values['type'] = type
        if self.is_studio():
            self.clear_caches()
        return super(IrQWeb, self)._render(template, values=values, **options)

    @api.model
    def load_template(self, view_id):
        element = self._get_template(int(view_id))[0]
        return etree.tostring(element)

    def _get_template(self, template):
        element, document, ref = super(IrQWeb, self)._get_template(template)
        if self.is_studio():
            view_id = self.env['ir.ui.view']._view_obj(template).id
            if not view_id:
                raise ValueError("Template '%s' undefined" % template)

            root = element.getroottree()
            basepath = len('/'.join(root.getpath(root.xpath('//*[@t-name]')[0]).split('/')[0:-1]))
            for node in element.iter(tag=etree.Element):
                node.set('data-oe-id', str(view_id))
                node.set('data-oe-xpath', root.getpath(node)[basepath:])
        return (element, document, ref)

    def _is_static_node(self, el, compile_context):
        return not self.is_studio() and super(IrQWeb, self)._is_static_node(el, compile_context)

    def is_studio(self):
        return self.env.context.get("STUDIO", False)

    def _compile_directive_options(self, el, compile_context, level):
        if self.is_studio():
            data_options = el.get("t-options")
            if data_options:
                el.set("data-oe-options", data_options)
        return super(IrQWeb, self)._compile_directive_options(el, compile_context, level)

    # def _compile_directive_field(self, el, compile_context, indent):
    #     if self.is_studio():
    #         el.set('oe-field', el.get('t-field'))
    #     res = super(IrQWeb, self)._compile_directive_field(el, compile_context, indent)
    #     return res

    # def _compile_directive_esc(self, el, compile_context, indent):
    #     if self.is_studio():
    #         el.set("oe-esc", el.get("t-esc"))'        attrs[\\'oe-esc\\'] = \\'tax_totals[\\'formatted_amount_total\\']\\''
    #     return super(IrQWeb, self)._compile_directive_esc(el, compile_context, indent)

    def _compile_directive_att(self, el, compile_context, level):
        code = super(IrQWeb, self)._compile_directive_att(el, compile_context, level)
        if self.is_studio():
            if el.attrib.get('t-field', False):
                code.append(indent_code(f"attrs['oe-field'] = '{el.attrib['t-field']}'", level))
            if el.attrib.get('t-esc', False):
                code.append(indent_code(f'attrs["oe-esc"] ="{escape(str(el.attrib["t-esc"]))}"', level))
            code.append(indent_code("""
                    attrs['data-oe-context'] = values['json'].dumps({
                        key: values['type'](values[key]).__name__
                        for key in values.keys()
                        if  key
                            and key != 'true'
                            and key != 'false'
                            and not key.startswith('_')
                            and ('_' not in key or key.rsplit('_', 1)[0] not in values or key.rsplit('_', 1)[1] not in ['even', 'first', 'index', 'last', 'odd', 'parity', 'size', 'value'])
                            and (values['type'](values[key]).__name__ not in ['LocalProxy', 'function', 'method', 'Environment', 'module', 'type'])
                    })
                    """, level))
        return code
        # def _compile_all_attributes(self, el, options, indent, attr_already_created=False):
        # code = []
        # if True:
        #     # attr_already_created = True
        #     # code.append(indent_code(f"""
        #     #                     atts_value = {self._compile_expr(value)}
        #     #                     if isinstance(atts_value, dict):
        #     #                         attrs.update(atts_value)
        #     #                     elif isinstance(atts_value, (list, tuple)) and not isinstance(atts_value[0], (list, tuple)):
        #     #                         attrs.update([atts_value])
        #     #                     elif isinstance(atts_value, (list, tuple)):
        #     #                         attrs.update(dict(atts_value))
        #     #                     """, level))
        #     code = [indent_code("""
        #         attrs = {}
        #         attrs['data-oe-context'] = values['json'].dumps({
        #             key: values['type'](values[key]).__name__
        #             for key in values.keys()
        #             if  key
        #                 and key != 'true'
        #                 and key != 'false'
        #                 and not key.startswith('_')
        #                 and ('_' not in key or key.rsplit('_', 1)[0] not in values or key.rsplit('_', 1)[1] not in ['even', 'first', 'index', 'last', 'odd', 'parity', 'size', 'value'])
        #                 and (values['type'](values[key]).__name__ not in ['LocalProxy', 'function', 'method', 'Environment', 'module', 'type'])
        #         })
        #         """, level)]
        #
        # return code + super(IrQWeb, self)._compile_directive_att(el, compile_context, level)
