odoo.define('pos_custom.HeaderButton', function (require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');
    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;




    const HeaderButtonCustom = HeaderButton => class extends HeaderButton {
        async onClick() {

            const info = await this.env.pos.getClosePosInfo();
            var user = this.env.pos.user;
            if (info.isManager) {
                this.showPopup('ClosePosPopup', { info: info, keepBehind: true });

            }
            else {
                this.showPopup('CustomClosePosPopup', { info: info, keepBehind: true });
            }

        }



    };


    Registries.Component.extend(HeaderButton, HeaderButtonCustom);

    return HeaderButton;
});