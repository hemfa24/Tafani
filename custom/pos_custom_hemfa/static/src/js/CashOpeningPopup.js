odoo.define('pos_cash_opening_zero.CashOpeningPopup', function (require) {
    "use strict";
    const { useState } = owl;
    const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
    const Registries = require("point_of_sale.Registries")

    const CashOpeningZero = (CashOpeningPopup) =>
        class extends CashOpeningPopup {
            setup() {
                super.setup();
                if (this.env.pos.config.default_cash) {

                    this.manualInputCashCount = null;
                    this.state = useState({
                        notes: "",
                        openingCash: this.env.pos.config.opening_cash,
                        displayMoneyDetailsPopup: false,
                    });
                }
            }
        };

    Registries.Component.extend(CashOpeningPopup, CashOpeningZero);

    return CashOpeningZero
});