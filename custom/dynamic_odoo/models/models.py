from odoo.models import BaseModel, AbstractModel
from odoo import api
from lxml import etree
from odoo.tools import frozendict

_search_read = BaseModel.search_read
_onchange = BaseModel.onchange
_read = BaseModel.read


@api.model
def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
    result = _search_read(self, domain=domain, fields=fields, offset=offset, limit=limit, order=order, **read_kwargs)
    # Odoo_Studio
    if self.env.context.get("Studio", False) or self.env.context.get("planning", False):
        for res in result:
            for fname in res:
                if type(res[fname]) == dict:
                    if any([(True if type(x) == frozendict else False) for x in res[fname].keys()]):
                        res[fname] = None
    return result


def read(self, fields=None, load='_classic_read'):
    result = _read(self, fields=fields, load=load)
    if self.env.context.get("Studio", False):
        for res in result:
            for fname in res:
                if type(res[fname]) == dict:
                    if any([(True if type(x) == frozendict else False) for x in res[fname].keys()]):
                        res[fname] = None
    return result


def onchange(self, values, field_name, field_onchange):
    result = _onchange(self, values, field_name, field_onchange)
    # Odoo_Studio
    if self.env.context.get("Studio", False):
        for fname in result['value']:
            # for fname in res:
            if isinstance(result['value'][fname], dict):
                if any([(True if isinstance(x, frozendict) else False) for x in result['value'][fname].keys()]):
                    result['value'][fname] = None
    return result


def fnc_button_studio(self):
    context = self.env.context
    button_action = context.get("BUTTON_ACTION", False) or context.get("params", {}).get('BUTTON_ACTION', False)
    if button_action:
        action = self.env['base.automation'].search([('id', '=', button_action)])
        if action:
            action.with_context(__action_done={})._process(self)


BaseModel.fnc_button_studio = fnc_button_studio
BaseModel.search_read = search_read
BaseModel.onchange = onchange
BaseModel.read = read
# _fields_view_get = AbstractModel.fields_view_get
#
#
# AbstractModel.fnc_button_studio = fnc_button_studio
#
#
# @api.model
# def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#     res = _fields_view_get(self, view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#     # only use in Studio Edit
#     res['fieldsGet'] = self.env[self._name].fields_get()
#     action_id = self.env.context.get("action", False) or self.env.context.get("action_id", False) or self.env.context.get("params", {}).get("action", False)
#     if 'studio.view.center' in self.env.registry.models and res and action_id:
#         view_ref = self.env.context.get(view_type + "_view_ref", False)
#         ui_view = self.env['ir.ui.view']
#         model_view = 'studio.view.center'
#         domain = [['id', '=', -1]]
#         if 'view_id' in res:
#             domain = [['view_id', '=', res['view_id']], ['action_id', '=', action_id], ['arch', '!=', False]]
#         elif 'view_id' not in res and view_ref and view_ref.find("odoo_studio") >= 0:
#             domain = [['view_key', '=', view_ref.replace("odoo_studio.", "")]]
#         view_center = self.env[model_view].search(domain, limit=1)
#     # if 'studio.view.center' in self.env.registry.models and res and 'view_id' in res and action_id:
#     #     ui_view = self.env['ir.ui.view']
#     #     model_view = 'studio.view.center'
#     #     view_center = self.env[model_view].search(
#     #         [['view_id', '=', res['view_id']], ['action_id', '=', action_id], ['arch', '!=', False]], limit=1)
#
#
#         # old_fields = res['fields']
#         # only use in Studio
#         # for field_name in old_fields:
#         #     old_field = old_fields[field_name]
#         #     if 'views' in old_field and len(old_field['views'].keys()):
#         #         fields_get = self.env[old_field['relation']].fields_get()
#         #         for view in old_field['views'].values():
#         #             view['fieldsGet'] = fields_get
#         res['arch_original'] = res['arch']
#         if len(view_center):
#             x_arch, x_fields = ui_view.with_context(STUDIO=True).postprocess_and_fields(
#                 etree.fromstring(view_center.arch), model=self._name)
#
#             res['arch'] = x_arch
#             res['fields'] = x_fields
#             res['view_studio_id'] = view_center.id
#             res['view_key'] = view_center.view_key
#             res['arch_original'] = x_arch
#         # only use in Studio
#         for field_name in res['fields']:
#             x_field = res['fields'][field_name]
#             if 'views' in x_field and len(x_field['views'].keys()):
#                 fields_get = self.env[x_field['relation']].fields_get()
#                 for view in x_field['views'].values():
#                     view['fieldsGet'] = fields_get
#
#     return res
#
#
# AbstractModel.fields_view_get = fields_view_get
