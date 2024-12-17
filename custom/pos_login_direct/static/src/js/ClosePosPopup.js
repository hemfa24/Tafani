odoo.define('pos_login_direct.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const PosLoginDirectClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            async closeSession() {
                if (this.env.pos.user.close_cash_popup) {
                    return window.location = '/web/session/logout'
                }
                await super.closeSession()
                if (this.env.pos.user.pos_logout_direct) {
                    return window.location = '/web/session/logout'
                }
            }
        };

    Registries.Component.extend(ClosePosPopup, PosLoginDirectClosePosPopup);

    return ClosePosPopup;
});
