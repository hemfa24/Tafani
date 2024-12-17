from odoo import models, api, fields
from odoo.addons.base.models import ir_ui_view
from odoo.tools.safe_eval import safe_eval
from lxml import etree
from odoo.tools import lazy, lazy_property, frozendict, str2bool
import collections
import random
import json
from odoo.exceptions import UserError

super_transfer_node_to_modifiers = ir_ui_view.transfer_node_to_modifiers


def inherit_transfer_node_to_modifiers(node, modifiers):
    attrs_original = node.attrib.get("attrs_original", False)
    attrs = node.attrib.get('attrs', None)
    attr_original = node.attrib.get("attr_original", False)
    attr_rewrite = {}
    # ======
    if not attrs_original and attrs:
        node.set("attrs_original", attrs)
    if not node.attrib.get("attrs", False) and attrs_original:
        node.set("attrs", attrs_original)
    # ======
    if attr_original:
        attr_original = json.loads(attr_original)
        for attr in ('invisible', 'readonly', 'required'):
            attr_val = node.get(attr, None)
            if attr_val is not None:
                attr_rewrite[attr] = attr_val
                # attr_original[attr] = attr_val
            elif attr in attr_original:
                node.set(attr, attr_original[attr])
        # node.set('attr_original', json.dumps(attr_original))

    if not attr_original:
        attr_original = {}
        for attr in ('invisible', 'readonly', 'required'):
            value_str = node.attrib.get(attr, None)
            if value_str:
                attr_original[attr] = value_str
        if attr_original:
            node.set('attr_original', json.dumps(attr_original))
    # ======
    super_transfer_node_to_modifiers(node, modifiers)
    for attr in attr_rewrite.keys():
        node.set(attr, attr_rewrite[attr])
        modifiers[attr] = str2bool(attr_rewrite[attr])
    if node.get('props_modifier'):
        modifiers.update(safe_eval(node.get('props_modifier')))
    # if context.get("STUDIO", False):
    #     if node.get('props_modifier'):
    #         # for node.get('props_modifier')
    #         modifiers.update(safe_eval(node.get('props_modifier')))
    #     if node.get("invisible") and (any(parent.tag == 'tree' for parent in node.iterancestors()) and not any(
    #             parent.tag == 'header' for parent in node.iterancestors())):
    #         v = str(safe_eval(node.get("invisible"), {'context': context or {}}))
    #         if v.find("[") >= 0:
    #             modifiers["invisible"] = v
    #             del modifiers["column_invisible"]


ir_ui_view.transfer_node_to_modifiers = inherit_transfer_node_to_modifiers


class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        res = super(Model, self).get_views(views, options)
        return res

    # @api.model
    # def get_views(self, views, options=None):
    #     """ Returns the fields_views of given views, along with the fields of
    #     the current model, and optionally its filters for the given action.
    #
    #     :param views: list of [view_id, view_type]
    #     :param dict options: a dict optional boolean flags, set to enable:
    #
    #         ``toolbar``
    #             includes contextual actions when loading fields_views
    #         ``load_filters``
    #             returns the model's filters
    #         ``action_id``
    #             id of the action to get the filters, otherwise loads the global
    #             filters or the model
    #
    #     :return: dictionary with fields_views, fields and optionally filters
    #     """
    #     options = options or {}
    #     result = {}
    #
    #     result['views'] = {
    #         v_type: self.get_view(
    #             v_id, v_type if v_type != 'list' else 'tree',
    #             **options
    #         )
    #         for [v_id, v_type] in views
    #     }
    #
    #     models = {}
    #     for view in result['views'].values():
    #         for model, model_fields in view.pop('models').items():
    #             models.setdefault(model, set()).update(model_fields)
    #
    #     result['models'] = {}
    #
    #     for model, model_fields in models.items():
    #         result['models'][model] = self.env[model].fields_get(
    #             allfields=model_fields, attributes=self._get_view_field_attributes()
    #         )
    #
    #     # Add related action information if asked
    #     if options.get('toolbar'):
    #         for view in result['views'].values():
    #             view['toolbar'] = {}
    #
    #         bindings = self.env['ir.actions.actions'].get_bindings(self._name)
    #         for action_type, key in (('report', 'print'), ('action', 'action')):
    #             for action in bindings.get(action_type, []):
    #                 view_types = (
    #                     action['binding_view_types'].split(',')
    #                     if action.get('binding_view_types')
    #                     else result['views'].keys()
    #                 )
    #                 for view_type in view_types:
    #                     view_type = view_type if view_type != 'tree' else 'list'
    #                     if view_type in result['views']:
    #                         result['views'][view_type]['toolbar'].setdefault(key, []).append(action)
    #
    #     if options.get('load_filters') and 'search' in result['views']:
    #         result['views']['search']['filters'] = self.env['ir.filters'].get_filters(
    #             self._name, options.get('action_id')
    #         )
    #
    #     return result

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Model, self).get_view(view_id=view_id, view_type=view_type, **options)
        res['fieldsGet'] = self.env[self._name].fields_get()
        action_id = self.env.context.get("action", False) or self.env.context.get("action_id",
                                                                                  False) or self.env.context.get(
            "params", {}).get("action", False) or options.get("action_id", False)
        if 'studio.view.center' in self.env.registry.models and res and action_id:
            view_ref = self.env.context.get(view_type + "_view_ref", False)
            ui_view = self.env['ir.ui.view']
            model_view = 'studio.view.center'
            domain = [['id', '=', -1]]
            if 'id' in res:
                domain = [['view_id', '=', res['id']], ['action_id', '=', action_id], ['arch', '!=', False]]
                if not res['id']:
                    domain.append(['res_model', '=', self._name])
                    domain.append(['view_type', '=', view_type])
            elif 'id' not in res and view_ref and view_ref.find("odoo_studio") >= 0:
                domain = [['view_key', '=', view_ref.replace("odoo_studio.", "")]]
            view_center = self.env[model_view].search(domain, limit=1)
            # if 'studio.view.center' in self.env.registry.models and res and 'view_id' in res and action_id:
            #     ui_view = self.env['ir.ui.view']
            #     model_view = 'studio.view.center'
            #     view_center = self.env[model_view].search(
            #         [['view_id', '=', res['view_id']], ['action_id', '=', action_id], ['arch', '!=', False]], limit=1)

            # old_fields = res['fields']
            # only use in Studio
            # for field_name in old_fields:
            #     old_field = old_fields[field_name]
            #     if 'views' in old_field and len(old_field['views'].keys()):
            #         fields_get = self.env[old_field['relation']].fields_get()
            #         for view in old_field['views'].values():
            #             view['fieldsGet'] = fields_get
            res['arch_original'] = res['arch']
            if len(view_center):
                # x_arch, x_fields = ui_view.with_context(STUDIO=True).postprocess_and_fields(
                #     etree.fromstring(view_center.arch), model=self._name)

                x_arch, x_models = ui_view.with_context(STUDIO=True).postprocess_and_fields(
                    etree.fromstring(view_center.arch), model=self._name, **options)
                x_models = self._get_view_fields(view_type, x_models)
                x_models = frozendict({model: tuple(fields) for model, fields in x_models.items()})

                node = etree.fromstring(x_arch)
                node = ui_view._postprocess_access_rights(node)
                # node = self.env['ir.ui.view']._postprocess_context_dependent(node)
                res['arch'] = etree.tostring(node, encoding="unicode").replace('\t', '')
                res['models'] = x_models
                res['view_studio_id'] = view_center.id
                res['view_key'] = view_center.view_key
                res['arch_original'] = x_arch
            # only use in Studio
            # for field_name in res['fields']:
            #     x_field = res['fields'][field_name]
            #     if 'views' in x_field and len(x_field['views'].keys()):
            #         fields_get = self.env[x_field['relation']].fields_get()
            #         for view in x_field['views'].values():
            #             view['fieldsGet'] = fields_get
        return res


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('plan', 'Planning')], ondelete={'plan': 'cascade'})

    def _apply_groups(self, node, name_manager, node_info):
        groups = node.get('groups')
        res = super(IrUiView, self)._apply_groups(node, name_manager, node_info)
        if self.env.context.get("STUDIO", False) and groups:
            node.set('groups', groups)
        return res

    @api.constrains('arch_db')
    def _check_xml(self):
        if "view_center" in self.name:
            return True
        return super(IrUiView, self)._check_xml()

    def remove_view(self):
        self.env['ir.actions.act_window.view'].search([['view_id', 'in', self.ids]]).unlink()
        return self.unlink()

    @api.model
    def create_new_view(self, values):
        view_mode = values.get('view_mode', False)
        action_id = values.get('action_id', False)
        data = values.get("data", {})
        view_id = self.env['ir.ui.view'].create(data)
        if action_id:
            if view_mode == "search":
                self.env['ir.actions.act_window'].browse(action_id).write({'search_view_id': view_id.id})
            else:
                values_action_view = {'sequence': 100, 'view_id': view_id.id,
                                      'act_window_id': action_id, 'view_mode': view_mode}
                self.env['ir.actions.act_window.view'].create(values_action_view)
        return view_id.id

    def read(self, fields=None, load='_classic_read'):
        report_id = self.env.context.get("REPORT_ID", False)
        res = super(IrUiView, self).read(fields=fields, load=load)
        if len(self) == 1 and self.type == "qweb" and report_id:
            template = self.env['report.center'].search([['view_id', '=', self.id], ['report_id', '=', report_id]],
                                                        limit=1)
            if len(template):
                for view in res:
                    view['arch'] = template.xml
        return res

    def get_report_studio(self, report_id, view_id):
        template = self.env['report.center'].search([['view_id', '=', view_id], ['report_id', '=', report_id]], limit=1)
        if len(template):
            return template.xml
        return None

    def _combine(self, hierarchy: dict):
        report_id = self.env.context.get("REPORT_ID", False)
        arch_studio = self.get_report_studio(report_id, self.id)
        if not arch_studio:
            return super(IrUiView, self)._combine(hierarchy)
        self.ensure_one()
        assert self.mode == 'primary'

        combined_arch = etree.fromstring(arch_studio)
        if self.env.context.get('inherit_branding'):
            combined_arch.attrib.update({
                'data-oe-model': 'ir.ui.view',
                'data-oe-id': str(self.id),
                'data-oe-field': 'arch',
            })
        self._add_validation_flag(combined_arch)
        # queue = collections.deque(sorted(hierarchy[self], key=lambda v: v.mode))
        # while queue:
        #     view = queue.popleft()
        #     arch = etree.fromstring(view.arch)
        #     if view.env.context.get('inherit_branding'):
        #         view.inherit_branding(arch)
        #     self._add_validation_flag(combined_arch, view, arch)
        #     combined_arch = view.apply_inheritance_specs(combined_arch, arch)
        #
        #     for child_view in reversed(hierarchy[view]):
        #         if child_view.mode == 'primary':
        #             queue.append(child_view)
        #         else:
        #             queue.appendleft(child_view)

        return combined_arch

    @api.model
    def get_views_ok(self):
        return {
            # 'translation': [[self.env.ref('base.view_translation_dialog_tree').id, 'list'],
            #                 [self.env.ref('base.view_translation_search').id, 'search']],
            'controller': [[False, 'list'], [False, 'form']],
            'automation': [[False, 'list'], [False, 'form'],
                           [self.env.ref('base_automation.view_base_automation_search').id, 'search']],
            'access_control': [[False, 'list'], [False, 'form'],
                               [self.env.ref('base.ir_access_view_search').id, 'search']],
            'filter_rules': [[False, 'list'], [False, 'form'],
                             [self.env.ref('base.ir_filters_view_search').id, 'search']],
            'record_rules': [[False, 'list'], [False, 'form'], [self.env.ref('base.view_rule_search').id, 'search']]}

    def duplicate_template(self, old_report, new_report):
        new = self.copy()
        cloned_templates, new_key = self.env.context.get('cloned_templates', {}), '%s_cp_%s' % (
            new.key.split("_cp_")[0], random.getrandbits(30))
        self, studio_center = self.with_context(cloned_templates=cloned_templates), self.env['report.center']
        cloned_templates[new.key], arch_tree = new_key, etree.fromstring(self._read_template(self.id))

        for node in arch_tree.findall(".//t[@t-call]"):
            template_call = node.get('t-call')
            if '{' in template_call:
                continue
            if template_call not in cloned_templates:
                template_view = self.search([('key', '=', template_call)], limit=1)
                template_copy = template_view.duplicate_template(old_report, new_report)
                studio_view = studio_center.search([('view_id', '=', template_view.id), ('report_id', '=', old_report)],
                                                   limit=1)
                if studio_view:
                    studio_view.copy({'view_id': template_copy.id, 'report_id': new_report})
            node.set('t-call', cloned_templates[template_call])
        subtree = arch_tree.find(".//*[@t-name]")
        if subtree is not None:
            subtree.set('t-name', new_key)
            arch_tree = subtree
        new.write({
            'name': '%s Copy' % new.name,
            'key': new_key,
            'arch_base': etree.tostring(arch_tree, encoding='unicode'),
            'inherit_id': False,
        })
        return new

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(IrUiView, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        # only use in Studio Edit
        res['fieldsGet'] = self.env[self._name].fields_get()
        action_id = self.env.context.get("action", False) or self.env.context.get("action_id",
                                                                                  False) or self.env.context.get(
            "params", {}).get("action", False)
        if 'studio.view.center' in self.env.registry.models and res and action_id:
            view_ref = self.env.context.get(view_type + "_view_ref", False)
            ui_view = self.env['ir.ui.view']
            model_view = 'studio.view.center'
            domain = [['id', '=', -1]]
            if 'view_id' in res:
                domain = [['view_id', '=', res['view_id']], ['action_id', '=', action_id], ['arch', '!=', False]]
            elif 'view_id' not in res and view_ref and view_ref.find("odoo_studio") >= 0:
                domain = [['view_key', '=', view_ref.replace("odoo_studio.", "")]]
            view_center = self.env[model_view].search(domain, limit=1)
            # if 'studio.view.center' in self.env.registry.models and res and 'view_id' in res and action_id:
            #     ui_view = self.env['ir.ui.view']
            #     model_view = 'studio.view.center'
            #     view_center = self.env[model_view].search(
            #         [['view_id', '=', res['view_id']], ['action_id', '=', action_id], ['arch', '!=', False]], limit=1)

            # old_fields = res['fields']
            # only use in Studio
            # for field_name in old_fields:
            #     old_field = old_fields[field_name]
            #     if 'views' in old_field and len(old_field['views'].keys()):
            #         fields_get = self.env[old_field['relation']].fields_get()
            #         for view in old_field['views'].values():
            #             view['fieldsGet'] = fields_get
            res['arch_original'] = res['arch']
            if len(view_center):
                x_arch, x_fields = ui_view.with_context(STUDIO=True).postprocess_and_fields(
                    etree.fromstring(view_center.arch), model=self._name)

                res['arch'] = x_arch
                res['fields'] = x_fields
                res['view_studio_id'] = view_center.id
                res['view_key'] = view_center.view_key
                res['arch_original'] = x_arch
            # only use in Studio
            for field_name in res['fields']:
                x_field = res['fields'][field_name]
                if 'views' in x_field and len(x_field['views'].keys()):
                    fields_get = self.env[x_field['relation']].fields_get()
                    for view in x_field['views'].values():
                        view['fieldsGet'] = fields_get

        return res


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    model_id = fields.Many2one(string="Model", comodel_name="ir.model")

    def load_web_menus(self, debug):
        web_menus = super(IrUiMenu, self).load_web_menus(debug)
        obj_menus = self.browse(list(filter(lambda x: x != 'root', web_menus.keys())))

        for m in obj_menus:
            if m.id and m.id in web_menus:
                web_menus[m.id]['parent_id'] = [m.parent_id.id, m.parent_id.display_name]
                web_menus[m.id]['sequence'] = m.sequence

        return web_menus

    @api.model
    def create_new_app(self, values):
        app_name, menu_name, model_name, web_icon_data = values.get("app_name", False), values.get("object_name",
                                                                                                   False), values.get(
            "model_name", False), values.get("web_icon_data", False)
        if app_name:
            app_menu = self.create(
                {'name': app_name, 'parent_id': False, 'sequence': 100, 'web_icon_data': web_icon_data})
            parent_menu = self.create({'name': menu_name, 'parent_id': app_menu.id, 'sequence': 1})
            values['parent_id'] = parent_menu.id
            result = self.create_new_menu(values)
            result['menu_id'] = app_menu.id
            return result
        return False

    @api.model
    def create_new_model(self, model_des, model_name):
        model_values = {'name': model_des, 'model': model_name, 'state': 'manual',
                        'is_mail_thread': True, 'is_mail_activity': True,
                        'access_ids': [(0, 0, {'name': 'Group No One', 'group_id':
                            self.env.ref('base.group_no_one').id, "perm_read": True, "perm_write": True,
                                               "perm_create": True, "perm_unlink": True})]}
        return self.env['ir.model'].create(model_values).id

    @api.model
    def create_action_wd(self, model_name):
        # create action window
        action_window_values = {'name': 'New Model', 'res_model': model_name,
                                'view_mode': "tree,form", 'target': 'current', 'view_id': False}
        action_id = self.env['ir.actions.act_window'].create(action_window_values)
        # create tree view
        view_data = {"arch": "<tree><field name='id' /></tree>", "model": model_name,
                     "name": "{model}.tree.{key}".format(model=model_name, key=random.getrandbits(30))}
        view_id = self.env['studio.view.center'].create_new_view(
            {'view_mode': 'tree', 'action_id': action_id.id, "data": view_data})
        # create form view
        view_data = {
            "arch": "<form><header></header><sheet><div class='oe_button_box' name='button_box'></div><field name='id' invisible='True' /></sheet></form>",
            "model": model_name,
            "name": "{model}.form.{key}".format(model=model_name, key=random.getrandbits(30))}
        self.env['studio.view.center'].create_new_view(
            {'view_mode': 'form', 'action_id': action_id.id, "data": view_data})
        self.env['ir.model.data'].create({
            'module': 'odo_studio',
            'name': view_data['name'],
            'model': 'ir.ui.view',
            'res_id': view_id.id,
        })
        return action_id.id

    @api.model
    def create_new_menu(self, values):
        model_name, model_id, menu_name, empty_view = values.get("model_name", False), values.get("model_id", False), \
            values.get("object_name", False), values.get("empty_view", False)
        action_id, parent_id, sequence = False, values.get("parent_id", False), values.get("sequence", False)
        if model_name:
            model_id = self.create_new_model(menu_name, model_name)
            action_id = self.create_action_wd(model_name)
        else:
            model_obj = self.env['ir.model'].browse(model_id)
            if empty_view:
                action_id = self.create_action_wd(model_obj.model)
            else:
                action_ids = self.env['ir.actions.act_window'].search([('res_model', '=', model_obj.model)])
                if len(action_ids):
                    has_view = action_ids.filtered(lambda x: x.view_id != False)
                    if len(has_view):
                        has_tree = has_view.filtered(lambda x: (x.view_mode or "").find("tree") >= 0)
                        action_ids = has_tree if len(has_tree) else has_view
                    action_id = action_ids[0].id
        # create menu
        if model_id:
            menu = self.create({'name': menu_name, 'parent_id': parent_id, 'sequence': sequence or 1,
                                'action': '%s,%s' % ('ir.actions.act_window', action_id)})
            return {'action_id': action_id, 'menu_id': menu.id}
        return False

    @api.model
    def update_menu(self, menu_update, menu_delete):
        self.browse(menu_delete).unlink()
        for menu in menu_update:
            self.browse(int(menu)).write(menu_update[menu])

    @api.model
    def get_form_view_id(self):
        return self.env.ref('dynamic_odoo.ir_ui_menu_studio_form_view').id
