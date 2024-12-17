odoo.define('dynamic_odoo.basic', function (require) {
    "use strict";

    var core = require('web.core');
    var BasicModel = require('web.BasicModel');
    var BasicView = require('web.BasicView');
    var BasicRenderer = require('web.BasicRenderer');
    const widgetRegistry = require('web.widget_registry');
    const {registry} = require('@web/core/registry');
    const widgetRegistryOwl = require('web.widgetRegistry');
    const Registry = require("web.Registry");
    const WidgetWrapper = require("web.WidgetWrapper");
    const {Component} = owl;

    const spGet = widgetRegistry.get.bind(widgetRegistry);

    widgetRegistry.get = (key) => {
        if (!(key in widgetRegistry.map) && odoo.studio) {
            if (registry.category("view_widgets").get(key)) {
                return registry.category("view_widgets").get(key);
            }
        }
        return spGet(key);
    }

    BasicRenderer.include({
        _renderWidget: function (record, node) {
            if (odoo.studio) {
                const name = node.attrs.name;
                const Widget = widgetRegistryOwl.get(name) || widgetRegistry.get(name);
                const legacy = !(Widget.prototype instanceof Component);
                let widget;
                if (legacy) {
                    widget = new Widget(this, record, node, {mode: this.mode});
                } else {
                    widget = new WidgetWrapper(this, Widget, {
                        record,
                        node,
                        env: odoo.studio.env,
                        options: {mode: this.mode},
                    });
                }

                this.widgets.push(widget);

                // Prepare widget rendering and save the related promise
                let def;
                if (legacy) {
                    def = widget._widgetRenderAndInsert(function () {
                    });
                } else {
                    def = widget.mount(document.createDocumentFragment());
                }
                this.defs.push(def);
                var $el = $('<div>');

                var self = this;
                def.then(function () {
                    self._handleAttributes(widget.$el, node);
                    self._registerModifiers(node, record, widget);
                    widget.$el.addClass('o_widget');
                    $el.replaceWith(widget.$el);
                });

                return $el;
            }
            this._super(record, node);
        },
    });

    BasicView.include({
        init: function (viewInfo, params) {
            this._super(viewInfo, params);
            if (params.fromEdit) {
                const {loadParams} = params;
                Object.assign(this.loadParams, loadParams);
            }
        },
        _processNode: function (node, fv) {
            const res = this._super(node, fv);
            if (node.tag === 'field') {
                const viewType = fv.type, fieldsInfo = fv.fieldsInfo[viewType], fields = fv.viewFields;
                const field = fields[node.attrs.name], fieldInfo = fieldsInfo[node.attrs.name];
                if (["many2many", "one2many"].includes(field.type) && Object.keys(fieldInfo.views).length) {
                    // const getViewType = (viewType) => viewType == "list" ? "tree" : viewType;
                    Object.values(fieldInfo.views).map((view) => {
                        // const viewType = getViewType(view.type);
                        if (!fv['view_studio_id'] && viewType in field.views) {
                            view.arch_base = field.views[view.type].arch;
                        }
                        view.arch_original = field.views[view.type].arch;
                        node.children.push(view.arch);
                    });
                }
            }
            return res;
        }
    });

    BasicModel.include({
        _getFieldNames: function (element, options) {
            const fieldsInfo = element.fieldsInfo, viewType = options && options.viewType || element.viewType,
                fields = fieldsInfo && fieldsInfo[viewType] || {},
                newFields = Object.values(fields).filter((field) => field._new).map((field) => field.name);
            if (newFields.length) {
                return Object.keys(fields).filter((fieldName) => !newFields.includes(fieldName));
            }
            return this._super(element, options);
        },
        load: function (params) {
            if (params.localData) {
                Object.assign(this.localData, params.localData)
            }
            return this._super(params);
        }
    });
});
