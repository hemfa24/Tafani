odoo.define("sh_pos_wh_stock_adv.chrome", function (require) {
    "use strict";

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require("point_of_sale.Registries");

    const PosResChrome = (Chrome) =>
        class extends Chrome {
            
            _buildChrome() {
                super._buildChrome();
                var self = this;
                this.env.services['bus_service'].addEventListener('notification', ({ detail: notifications }) => {
                    if (self && self.env && self.env.pos && self.env.pos.config && self.env.pos.config.sh_display_stock && self.env.pos.config.sh_update_real_time_qty ) {
                        if (notifications) {

                            _.each(notifications, function (each_notification) {
                                if (each_notification && each_notification["payload"] && each_notification["payload"][0]) {
                                    if (
                                        each_notification["payload"][0]["product_id"] &&
                                        each_notification["payload"][0]["product_id"][0] &&
                                        each_notification["payload"][0]["location_id"] &&
                                        each_notification["payload"][0]["location_id"][0] &&
                                        each_notification["payload"][0]["location_id"][0] == self.env.pos.config.sh_pos_location[0]
                                    ) {
                                        if (
                                            self &&
                                            self.env &&
                                            self.env.pos &&
                                            self.env.pos.db &&
                                            self.env.pos.db.quant_by_product_id &&
                                            self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]] &&
                                            self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]][each_notification["payload"][0]["location_id"][0]]
                                        ) {
                                            if (each_notification["payload"][0]["manual_update"]){
                                                each_notification["payload"][0]["manual_update"]
                                            }else{
                                                var productObj = self.env.pos.db.product_by_id[each_notification["payload"][0]['product_id'][0]] 
                                                if (productObj.qty_available < 1){
                                                    productObj.qty_available = each_notification["payload"][0]["quantity"]
                                                }
                                                self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]][each_notification["payload"][0]["location_id"][0]] = each_notification["payload"][0]["quantity"];
                                            }
                                        } else {
                                            if (!self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]]) {
                                                
                                                self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]] = {};
                                                if (each_notification["payload"][0]["manual_update"] ){
                                                    each_notification["payload"][0]["manual_update"] 
                                                }else{
                                                    self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]][each_notification["payload"][0]["location_id"][0]] = each_notification["payload"][0]["quantity"];
                                                }
                                            } else if (
                                                self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]] &&
                                                !self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]][each_notification["payload"][0]["location_id"][0]]
                                                ) {
                                                    if (each_notification["payload"][0]["manual_update"] ){
                                                        each_notification["payload"][0]["manual_update"] 
                                                    }else{
                                                    self.env.pos.db.quant_by_product_id[each_notification["payload"][0]["product_id"][0]][each_notification["payload"][0]["location_id"][0]] = each_notification["payload"][0]["quantity"];
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        }
                    }
                } );
            }
        };

    Registries.Component.extend(Chrome, PosResChrome);

});
