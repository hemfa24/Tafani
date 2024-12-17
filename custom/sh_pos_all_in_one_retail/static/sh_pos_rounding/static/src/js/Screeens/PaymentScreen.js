
odoo.define("sh_pos_rounding.PaymentScreen", function (require) {
    "use strict";
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const { onMounted } = owl;

    const RoundingPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            setup() {
                super.setup();
                onMounted(() => {
                    if (this.env.pos.config.sh_enable_rounding) {
                        var order = this.env.pos.get_order();
                        $(this.el).find("#cb4").prop("checked", true);
                        order.set_is_payment_round(true);
                        var self = this;

                        // if toggle switch
                        $(this.el)
                            .find("#cb4")
                            .click(function () {
                                if ($(self.el).find("#cb4").prop("checked") == true) {
                                    order.set_is_payment_round(true);
                                    self.el.querySelector(".total").textContent = self.env.pos.format_currency(order.get_round_total_with_tax());
                                } else {
                                    self.el.querySelector(".total").textContent = self.env.pos.format_currency(order.get_total_with_tax());
                                    order.set_is_payment_round(false);
                                }
                            });
                    }
                });
            }
            // async validateOrder(isForceValidate) {
            //     if (await this._isOrderValid(isForceValidate)) {
            //         var order = this.currentOrder
            //         if (order.get_is_payment_round()) {
            //             var rounding_price = order.get_round_total_with_tax() - order.get_total_with_tax();
            //             order.set_rounding_price(rounding_price);
            //             var round_product = this.env.pos.db.get_product_by_id(this.env.pos.config.round_product_id[0]);
                        
            //             order.add_product(round_product, { quantity: 1, price: rounding_price });
            //         }

            //         // remove pending payments before finalizing the validation
            //         for (let line of this.paymentLines) {
            //             if (!line.is_done()) this.currentOrder.remove_paymentline(line);
            //         }
            //         await this._finalizeValidation();
            //     }
            // }
            addNewPaymentLine({ detail: paymentMethod }) {
                super.addNewPaymentLine(...arguments);
                $(this.el).find(".cb4_label").css("display", "none");
                $(this.el).find(".rounding_label").css("display", "none");
            }
        };

    Registries.Component.extend(PaymentScreen, RoundingPaymentScreen);

    return PaymentScreen;
});
