/** @odoo-module **/

const {registry} = require("@web/core/registry");
// const viewService = registry.category("services").get("view");
const data_manager = require("web.data_manager");
import {generateLegacyLoadViewsResult} from "@web/legacy/legacy_load_views";
import {deepCopy} from "@web/core/utils/objects";

function generateLegacyLoadViewsResultStudio(resModel, views, models) {
    const res = generateLegacyLoadViewsResult(resModel, views, models);
    for (const viewType in views) {
        const { view_key, view_studio_id, arch_original, fieldsGet } = views[viewType];
        res.fields_views[viewType].view_key = view_key;
        res.fields_views[viewType].view_studio_id = view_studio_id;
        res.fields_views[viewType].arch_original = arch_original;
        res.fields_views[viewType].fieldsGet = fieldsGet;
    }
    return res;
}

// const superStart = viewService.start.bind(viewService);
const superLoadViews = data_manager.load_views.bind(data_manager);
// viewService.start = (env, {orm}) => {
//     const viewS = superStart(env, {orm}), superLoadViews = viewS.loadViews;
//     viewS.loadViews = async (params, options) => {
//         if (!params.context) {
//             params.context = {};
//         }
//         if (!(params.context.action || params.context.action_id) && options.actionId) {
//             params.context.action = options.actionId;
//         }
//         if ((odoo['studio'] || {}).instance) {
//             params.context.STUDIO = true;
//         }
//
//         const loadViewsOptions = {
//             action_id: options.actionId || false,
//             load_filters: options.loadIrFilters || false,
//             toolbar: options.loadActionMenus || false,
//         };
//         if (env.isSmall) {
//             loadViewsOptions.mobile = true;
//         }
//         const {context, resModel, views} = params;
//         const filteredContext = Object.fromEntries(
//             Object.entries(context || {}).filter((k, v) => !String(k).startsWith("default_"))
//         );
//         const key = JSON.stringify([resModel, views, filteredContext, loadViewsOptions]);
//         if (!viewS.cache[key]) {
//             cache[key] = orm
//                 .call(resModel, "get_views", [], {context, views, options: loadViewsOptions})
//                 .then((result) => {
//                     const {models, views} = result;
//                     const modelsCopy = deepCopy(models); // for legacy views
//                     const viewDescriptions = {
//                         __legacy__: generateLegacyLoadViewsResult(resModel, views, modelsCopy),
//                         fields: models[resModel],
//                         relatedModels: models,
//                         views: {},
//                     };
//                     for (const [resModel, fields] of Object.entries(modelsCopy)) {
//                         const key = JSON.stringify(["fields", resModel, undefined, undefined]);
//                         cache[key] = Promise.resolve(fields);
//                     }
//                     for (const viewType in views) {
//                         const {arch, toolbar, id, filters, custom_view_id} = views[viewType];
//                         const viewDescription = {arch, id, custom_view_id, view_key};
//                         if (toolbar) {
//                             viewDescription.actionMenus = toolbar;
//                         }
//                         if (filters) {
//                             viewDescription.irFilters = filters;
//                         }
//                         viewDescriptions.views[viewType] = viewDescription;
//                     }
//                     return viewDescriptions;
//                 })
//                 .catch((error) => {
//                     delete cache[key];
//                     return Promise.reject(error);
//                 });
//         }
//         return cache[key];
//     }
//     return viewS;
// }

data_manager.load_views = async function ({model, context, views_descr}, options = {}) {
    const state = $.bbq.getState(true);
    context.action = state.action;
    return superLoadViews({model, context, views_descr}, options);
}

export const viewService = {
    dependencies: ["orm"],
    start(env, {orm}) {
        let cache = {};

        env.bus.addEventListener("CLEAR-CACHES", () => {
            cache = {};
            const processedArchs = registry.category("__processed_archs__");
            processedArchs.content = {};
            processedArchs.trigger("UPDATE");
        });

        /**
         * Loads fields information
         *
         * @param {string} resModel
         * @param {LoadFieldsOptions} [options]
         * @returns {Promise<object>}
         */
        async function loadFields(resModel, options = {}) {
            const key = JSON.stringify([
                "fields",
                resModel,
                options.fieldNames,
                options.attributes,
            ]);
            if (!cache[key]) {
                cache[key] = orm
                    .call(resModel, "fields_get", [options.fieldNames, options.attributes])
                    .catch((error) => {
                        delete cache[key];
                        return Promise.reject(error);
                    });
            }
            return cache[key];
        }

        /**
         * Loads various information concerning views: fields_view for each view,
         * fields of the corresponding model, and optionally the filters.
         *
         * @param {LoadViewsParams} params
         * @param {LoadViewsOptions} [options={}]
         * @returns {Promise<ViewDescriptions>}
         */
        async function loadViews(params, options = {}) {
            const loadViewsOptions = {
                action_id: options.actionId || false,
                load_filters: options.loadIrFilters || false,
                toolbar: options.loadActionMenus || false,
            };
            if (env.isSmall) {
                loadViewsOptions.mobile = true;
            }
            const {context, resModel, views} = params;
            const filteredContext = Object.fromEntries(
                Object.entries(context || {}).filter((k, v) => !String(k).startsWith("default_"))
            );
            const key = JSON.stringify([resModel, views, filteredContext, loadViewsOptions]);
            if (!cache[key]) {
                cache[key] = orm
                    .call(resModel, "get_views", [], {context, views, options: loadViewsOptions})
                    .then((result) => {
                        const {models, views} = result;
                        models[resModel] = Object.values(views)[0].fieldsGet;
                        const modelsCopy = deepCopy(models);
                        const viewDescriptions = {
                            __legacy__: generateLegacyLoadViewsResultStudio(resModel, views, modelsCopy),
                            fields: models[resModel],
                            relatedModels: models,
                            views: {},
                        };
                        for (const viewType in viewDescriptions.__legacy__.fields_views) {
                            const viewInfo = viewDescriptions.__legacy__.fields_views[viewType], {fields} = viewInfo;
                            viewInfo.viewFields = fields;
                            viewInfo.fields = models[resModel];
                        }
                        for (const [resModel, fields] of Object.entries(modelsCopy)) {
                            const key = JSON.stringify(["fields", resModel, undefined, undefined]);
                            cache[key] = Promise.resolve(fields);
                        }
                        for (const viewType in views) {
                            const {arch, toolbar, id, filters, custom_view_id, view_studio_id, arch_original, view_key} = views[viewType];
                            const viewDescription = {arch, id, custom_view_id, view_studio_id, arch_original, view_key};
                            if (toolbar) {
                                viewDescription.actionMenus = toolbar;
                            }
                            if (filters) {
                                viewDescription.irFilters = filters;
                            }
                            viewDescriptions.views[viewType] = viewDescription;
                        }
                        return viewDescriptions;
                    })
                    .catch((error) => {
                        delete cache[key];
                        return Promise.reject(error);
                    });
            }
            return cache[key];
        }

        return {loadViews, loadFields};
    },
};

registry.category("services").add("viewStudio", viewService);

