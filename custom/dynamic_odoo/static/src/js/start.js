/** @odoo-module alias=dynamic_odoo.start**/

const ViewCenter = require('dynamic_odoo.ViewsCenter');
const base = require('dynamic_odoo.base');
const {useService} = require("@web/core/utils/hooks");
const rootWidget = require('root.widget');
import legacyEnv from 'web.commonEnv';
const { Component, useChildSubEnv, useSubEnv, onMounted } = owl;


var StudioResource = base.WidgetBase.extend({
    init: function (parent, params = {}) {
        this._super(parent, params);
    },
    start: async function () {
        const fieldWidgets = await this.getReportFieldWidget();
        odoo['studio'].fieldWidgetOptions = fieldWidgets;
        odoo['studio'].models = await this.getModels();
        odoo['studio'].views = await this.getViews();
    },
    getViews: async function () {
        const views = await this['_rpc']({
            model: "ir.ui.view",
            method: 'get_views_ok',
            fields: [],
            domain: []
        });
        return views;
    },
    getModels: async function () {
        const models = await this['_rpc']({
            model: "ir.model",
            method: 'search_read',
            fields: ['id', 'model', 'display_name'],
            domain: []
        }), prepareData = {};
        models.map((model) => {
            prepareData[model.model] = model;
        });
        return prepareData;
    },
    getReportFieldWidget: function () {
        return this['_rpc']({
            model: "report.center",
            method: 'get_field_widget',
            args: [],
            kwargs: {},
        });
    },
});

export default class StudioEditor extends Component {
    setup() {
        var self = this;
        this.actionService = useService("action");
        this.viewService = useService("view");
        this.viewServiceStudio = useService("viewStudio");
        this.menuService = useService("menu");
        this.title = useService("title");
        this.ajax = useService("rpc");
        this.user = useService("user");
        // useSubEnv(legacyEnv);
        useService("legacy_service_provider");
        onMounted(async () => {
            await self.loadStudioMode();
        });
    }

    loadStudioMode = async () => {
        odoo.studio = {env: this.env, state: $.bbq.getState(true)};
        await (new StudioResource(rootWidget, {})).start();
        const newView = new ViewCenter(rootWidget, {
            service: {action: this.actionService, view: this.viewService, viewSt: this.viewServiceStudio},
            step: 'setup',
            typeEdit: "views",
            title: "Columns Setup",
            viewType: odoo['studio'].state.view_type,
        });
        newView.__parentedParent.__owl__ = {};
        odoo['studio'].instance = newView;
        odoo.rootStudio = this;
        newView.renderElement();
        $('body').addClass("editMode");
        $(this.__owl__.bdom.el).append(newView.$el);
    }
}

StudioEditor.template = "dynamic_odoo.StudioEditor";
