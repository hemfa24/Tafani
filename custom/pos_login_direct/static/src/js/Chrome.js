odoo.define('pos_login_direct.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosLoginDirectChrome = (Chrome) =>
        class extends Chrome {
            async _closePos() {
                if (this.env.pos && this.env.pos.user && this.env.pos.user.close_cash_popup) {
                    return window.location = '/web/session/logout'
                }
                await super._closePos()
                if (this.env.pos && this.env.pos.user && this.env.pos.user.pos_logout_direct) {
                    return window.location = '/web/session/logout'
                }
            }
        };

    Registries.Component.extend(Chrome, PosLoginDirectChrome);

    return Chrome;
});
