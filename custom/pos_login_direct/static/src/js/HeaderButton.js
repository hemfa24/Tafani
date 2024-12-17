odoo.define('pos_login_direct.HeaderButton', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');

    const PosLoginDirectHeaderButton = (HeaderButton) => class extends HeaderButton {

        async onClick() {
            if (this.env.pos.user.close_cash_popup) {
                return window.location = '/web/session/logout'
            } else {
                await super.onClick()
            }
        }
    };

    Registries.Component.extend(HeaderButton, PosLoginDirectHeaderButton);

    return HeaderButton;
});
