odoo.define('pos_cash_opening_zero.CashOpeningPopup', function (require) {
    "use strict";
    const { useState } = owl;
    const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
    const Registries = require("point_of_sale.Registries")
    const { useValidateCashInput } = require('point_of_sale.custom_hooks');

    const CashOpeningZero = (CashOpeningPopup) =>
        class extends CashOpeningPopup {
            // setup() {
            //     super.setup();
            //     this.manualInputCashCount = null;
            //     this.state = useState({
            //         notes: "",
            //         openingCash: this.env.pos.config.opening_cash,
            //         cash_register_balance_start: this.env.pos.config.opening_cash,
            //         displayMoneyDetailsPopup: false,
            //     });
            // }
            setup() {
                super.setup();
                this.manualInputCashCount = null;
                this.state = useState({
                    notes: "",
                    openingCash: this.env.pos.config.opening_cash || 0,
                    cash_register_balance_start: this.env.pos.config.opening_cash,
                    displayMoneyDetailsPopup: false,
                });
                useValidateCashInput("openingCashInput", this.env.pos.config.opening_cash);
            }
            async confirm() {
                this.env.pos.pos_session.cash_register_balance_start = this.env.pos.config.opening_cash;
                this.env.pos.pos_session.state = 'opened';
                this.rpc({
                    model: 'pos.session',
                    method: 'set_cashbox_pos',
                    args: [this.env.pos.pos_session.id, this.env.pos.config.opening_cash, this.state.notes],
                });
                super.confirm();
            }
        };

    Registries.Component.extend(CashOpeningPopup, CashOpeningZero);

    return CashOpeningZero
});