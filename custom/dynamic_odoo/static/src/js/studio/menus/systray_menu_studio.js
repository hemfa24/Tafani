/** @odoo-module **/

import Start from '@dynamic_odoo/js/start';
// const base = require('dynamic_odoo.base');
// const SysTrayMenu = require('web.SystrayMenu');
// const session = require('web.session');
import { session } from "@web/session";
const {mount, xml, Component} = owl;
import {templates} from "@web/core/assets";
import {useComponentToModel} from '@mail/component_hooks/use_component_to_model';
import {registerMessagingComponent} from '@mail/utils/messaging_component';
import {registry} from '@web/core/registry';

const systrayRegistry = registry.category('systray');


export class StudioIcon extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        // if (!systrayRegistry.contains('dynamic_odoo.StudioIcon')) {
        //     systrayRegistry.add('dynamic_odoo.StudioIcon', { Component: StudioIcon }, { sequence: 1 });
        // }
    }

    async onClickIcon() {
        // e.stopPropagation();
        // e.stopImmediatePropagation();
        const root = await
            mount(Start, document.getElementsByClassName("o_action_manager")[0], {
                env: this.env,
                templates: templates,
                position: "first-child"
            });
        root.render();
    }

    // bindAction: function () {
    //     this._super();
    //     this.$el.click(this.renderStudioMode.bind(this));
    // }
}

// if (session['showStudio']) {
//     StudioMode.prototype.sequence = 1;
//     SysTrayMenu.Items.push(StudioMode);
// }

StudioIcon.prototype.sequence = 1;
StudioIcon.components = {Start: Start};
StudioIcon.template = xml`<div class="o_mail_systray_item">
            <a class="aShowST" t-on-click="onClickIcon">
                <img width="12px" height="12px" src="/dynamic_odoo/static/src/img/studio_icon_mode.png" alt="Odoo Studio Icon" title="Toggle Studio" aria-label="Toggle Studio" />
            </a>
        </div>`;
if (session['showStudio']) {
    systrayRegistry.add("dynamic_odoo.StudioIcon", {Component: StudioIcon});
}


// StudioIcon.template = "dynamic_odoo.StudioIcon";

// SysTrayMenu.Items.push(StudioIcon);

// registerMessagingComponent(StudioIcon);

// Object.assign(ActivityMenuView, {
//     props: { record: Object },
//     template: 'dynamic_odoo.StudioIcon',
// });

// registerMessagingComponent(ActivityMenuView);

//
// import { useModels } from '@mail/component_hooks/use_models';
// // ensure components are registered beforehand.
// import '@mail/components/call_systray_menu/call_systray_menu';
// import { getMessagingComponent } from "@mail/utils/messaging_component";
//
// const { Component } = owl;

// export class StudioMode extends Component {
//
//     /**
//      * @override
//      */
//     // setup() {
//     //     // useModels();
//     //     super.setup();
//     // }
//
//     // get messaging() {
//     //     return this.env.services.messaging.modelManager.messaging;
//     // }
//
// }
//
// StudioMode.template = "Studio.Icon";
// // Object.assign(StudioMode, {
// //     // components: { CallSystrayMenu: getMessagingComponent('CallSystrayMenu') },
// //     template: 'Studio.Icon',
// // });
//
// SysTrayMenu.Items.push(StudioMode);


// var StudioMode = base.WidgetBase.extend({
//     template: "Studio.Icon",
//     init: function (parent, params = {}) {
//         this._super(parent, params);
//     },
//     renderStudioMode: async function (e) {
//         e.stopPropagation();
//         e.stopImmediatePropagation();
//         const root = await
//             mount(start, {
//                 env: odoo['__WOWL_DEBUG__'].root.env,
//                 target: document.getElementsByClassName("o_action_manager")[0],
//                 position: "first-child"
//             });
//         root.render();
//     },
//     bindAction: function () {
//         this._super();
//         this.$el.click(this.renderStudioMode.bind(this));
//     }
// });
//
// StudioMode.prototype.sequence = 1;
// SysTrayMenu.Items.push(StudioMode);

// if (session['showStudio']) {
//     StudioMode.prototype.sequence = 1;
//     SysTrayMenu.Items.push(StudioMode);
// }
