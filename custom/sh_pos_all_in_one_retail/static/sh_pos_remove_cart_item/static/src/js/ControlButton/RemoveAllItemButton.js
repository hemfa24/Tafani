odoo.define("sh_pos_order_signature.ActionButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const ProductScreen = require("point_of_sale.ProductScreen");

    class RemoveAllItemButton extends PosComponent {
        constructor() {
            super(...arguments);
        }
        onClick() {
            var self = this;
            if (this.env.pos.get_order() && this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0) {
                var orderlines = this.env.pos.get_order().get_orderlines();
                _.each(orderlines, function (each_orderline) {
                    if (self.env.pos.get_order().get_orderlines()[0]) {
                        self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                    }
                });
                
                /* For product item count badge */
                this.env.pos.get_order().product_with_qty={}
                _.each(this.env.pos.get_order().get_orderlines(),(line)=>{line.set_quantity(line.quantity)});
            } else {
                self.showPopup('ErrorPopup', { 
                    title: 'Products !',
                    body: 'Cart is Empty !'
                })
            }
        }
    }
    RemoveAllItemButton.template = "RemoveAllItemButton";
    ProductScreen.addControlButton({
        component: RemoveAllItemButton,
        condition: function () {
            return this.env.pos.config.sh_remove_all_item;
        },
    });
    Registries.Component.add(RemoveAllItemButton);

    return RemoveAllItemButton
});
