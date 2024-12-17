odoo.define('pos_custom.CustomRewardButtons', function (require) {
    'use strict';

    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const { posbus } = require('point_of_sale.utils');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Widget = require('web.Widget');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const { identifyError } = require('point_of_sale.utils');
    const { ConnectionLostError, ConnectionAbortedError } = require('@web/core/network/rpc_service')
    const { useState } = owl;


    class CustomRewardButtons extends AbstractAwaitablePopup {

        setup() {
            super.setup();
            useListener('btn_custom_close-product', this._close_session_from_admin);
        }

        _close_session_from_admin() {
            const info = this.env.pos.getClosePosInfo();
            this.showPopup('ClosePosPopup', { info: info, keepBehind: true });
        }
    }
    Registries.Component.add(CustomRewardButtons);
    return CustomRewardButtons;
});

