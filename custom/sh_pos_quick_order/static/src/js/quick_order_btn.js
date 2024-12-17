odoo.define('sh_pos_quick_order.quick_order_btn', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");

    class shQuickOrder extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
       
        async onClick() {
            var self = this
            if ($(".product-screen").is(":visible") && this.env.pos.config.sh_is_enable_quick_order) {
                let Order = this.env.pos.get_order()
                if (Order.get_orderlines() && Order.get_orderlines().length > 0) {
                    $(".pay").trigger("click");
                    if (self.env.pos.config.sh_quick_customer) {
                        var Client = self.env.pos.db.get_partner_by_id(self.env.pos.config.sh_quick_customer[0])
                        Order.set_partner(Client)

                        if (self.env.pos.config.sh_quick_customer && self.env.pos.config.sh_is_enable_quick_invoice) {
                            Order.to_invoice = true
                        }
                    }

                    var sh_payment_line = self.env.pos.payment_methods_by_id[self.env.pos.config.sh_is_quick_payment_method[0]]
                    Order.add_paymentline(sh_payment_line)

                    setTimeout(() => {
                        $(".payment-screen").find(".next").trigger("click");
                    }, 10);

                } else {
                    self.showPopup('ErrorPopup', {
                        title: "No Orderline !",
                        body: 'Please Add Product in Cart !'
                    })
                }
            }
        }
    }
    shQuickOrder.template = 'shQuickOrder';

    ProductScreen.addControlButton({
        component: shQuickOrder,
        condition: function () {
            return this.env.pos.config.sh_is_enable_quick_order;
        },
    });
    Registries.Component.add(shQuickOrder);

    return shQuickOrder;
});
