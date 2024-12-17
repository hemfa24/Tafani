odoo.define("sh_pos_theme_responsive.product_screen", function (require) {
    "use strict";

    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const { onMounted, onWillUnmount, useRef} = owl;


    const PosProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            setup() {
                super.setup()
                var self = this;
                if (this.env.pos.pos_theme_settings_data[0] && this.env.pos.pos_theme_settings_data[0].sh_pos_switch_view) {

                    this.env.pos.product_view;

                    if (this.env.pos.pos_theme_settings_data[0].sh_pos_switch_view == false) {
                        $(".sh_switch_view_icon").hide();
                    } else {
                        if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "grid_view") {
                            this.env.pos.product_view = "grid";
                        } else if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "list_view") {
                            this.env.pos.product_view = "list";
                        }
                    }
                }
                setTimeout(() => {
                    this.env.pos.product_view;

                    if (this.env.pos.pos_theme_settings_data[0].sh_pos_switch_view == false) {
                        $(".sh_switch_view_icon").hide();
                    } else {
                        if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "grid_view") {
                            $(".product_grid_view").addClass("highlight");
                            $(".product_list").hide();
                        } else if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "list_view") {
                            $(".product_list_view").addClass("highlight");
                            $(".product_grid").hide();
                        }
                    }

                    var owl = $('.owl-carousel');
                    owl.owlCarousel({
                        loop: false,
                        nav: true,
                        margin: 10,
                        responsive: {
                            0: {
                                items: 2
                            },
                            600: {
                                items: 3
                            },
                            960: {
                                items: 5
                            },
                            1200: {
                                items: 6
                            }
                        }
                    });
                    owl.on('mousewheel', '.owl-stage', function (e) {
                        if (e.originalEvent.wheelDelta > 0) {
                            owl.trigger('next.owl');
                        } else {
                            owl.trigger('prev.owl');
                        }
                        e.preventDefault();
                    });
                }, 20);
                // For product item count badge
                // _.each(this.env.pos.get_order().get_orderlines(),(line)=>line.set_quantity(line.quantity));
            }
            switchPane() {
                if (this.env.pos.pos_theme_settings_data[0].sh_pos_switch_view == false) {
                    $(".sh_switch_view_icon").hide();
                } else {
                    if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "grid_view") {
                        $(".product_grid_view").addClass("highlight");
                        $(".product_list").hide();
                        $(".rightpane").removeClass("sh_right_pane");
                        this.env.pos.product_view = "grid";
                    } else if (this.env.pos.pos_theme_settings_data[0].sh_default_view == "list_view") {
                        $(".product_list_view").addClass("highlight");
                        $(".product_grid").hide();
                        $(".rightpane").addClass("sh_right_pane");
                        this.env.pos.product_view = "list";
                    }
                }
                super.switchPane();
            }
            is_show_able(cb) {
                if(cb.name && (cb.name != 'RemoveDiscountButton' && cb.name != 'RemoveAllItemButton' && cb.name != 'DiscountButton')){
                    if(cb.name == 'RefundButton' && this.env.pos.config.enable_refund == false){
                        return false;
                    }else if(cb.name == 'ProductInfoButton' && this.env.pos.config.enable_info == false){
                        return false;
                    }else if(cb.name == 'AllNoteButton' && this.env.pos.config.enable_note == false){
                        return false;
                    }else if(cb.name == 'ChangeUOMButton' && this.env.pos.config.enable_change_uom == false){
                        return false;
                    }else if(cb.name == 'shQuickOrder' && this.env.pos.config.enable_quick_order == false){
                        return false;
                    }else if(cb.name == 'SetSaleOrderButton' && this.env.pos.config.enable_show_order == false){
                        return false;
                    }
                    return true;
                }else{
                    return false;
                }
            }
            async _clickProduct(event) {

                var self = this;
                const product = event.detail;
                if(!!this.env.pos.config.enable_auto_pro_uom){
                    var selectionList = [];
                    var line = this.env.pos.get_order().get_selected_orderline();
                    if(this.env.pos.config.sh_enable_multi_barcode && product.barcode_line_ids.length){
                        var selectionList = []
                        var barcode_line_ids = product.barcode_line_ids
                        for(let ids of barcode_line_ids){
                            const multi_barcode_by_id = this.env.pos.db.multi_barcode_by_id[ids]
                            if(multi_barcode_by_id){
                                let tempDic = {'barcode': multi_barcode_by_id}
                                let price_lst = this.env.pos.pricelists.filter((pricelist) => pricelist.id == multi_barcode_by_id.price_lst )
                                let unit = this.env.pos.units_by_id[multi_barcode_by_id.unit]

                                tempDic['price_lst'] = price_lst
                                tempDic['unit'] = unit

                                selectionList.push(tempDic);
                            }
                        }
                        selectionList = selectionList.map(pricelist => ({
                            id: pricelist.barcode.id,
                            label: pricelist.barcode.name,
                            isSelected: pricelist.id === 1,
                            item: pricelist.barcode,
                            'price': this.env.pos.format_currency(pricelist.barcode.price),
                            'price_lst': pricelist.price_lst ? pricelist.price_lst[0] : false,
                            'unit': pricelist.unit
                        }))
                    }
                    else{
                        if (line) {
                            var uom = line.get_unit();
                            if (uom) {
                                selectionList.push({ id: uom.id, isSelected: true, label: uom.display_name, item: uom });
                                var secondary_uom = line.get_secondary_unit();
                                if (secondary_uom != uom) {
                                    selectionList.push({ id: secondary_uom.id, isSelected: false, label: secondary_uom.display_name, item: secondary_uom });
                                }
                            }
                        }
                        _.each(selectionList, function (each_uom) {
                            if (each_uom.label === line.get_current_uom().name) {
                                each_uom.isSelected = true;
                            } else {
                                each_uom.isSelected = false;
                            }
                        });
                    }
                      if (barcode_line_ids && barcode_line_ids.length > 1) {
                            const { confirmed, payload: selectedUOM } = await this.showPopup("SelectionPopup", {
                                title: this.env._t("Select the UOM"),
                                list: selectionList,
                            });
                        }else{


                                const order = self.env.pos.get_order();
                                const selectedOrderline = order.get_selected_orderline();

                                if (selectedOrderline && selectedOrderline.product.id === product.id) {
                                    // If the selected orderline matches the scanned product
                                    selectedOrderline.set_quantity(selectedOrderline.quantity + 1);
                                } else {
                                    // If the scanned product is not the selected product
                                    const existingLine = order.get_orderlines().find(line => line.product.barcode == product.barcode);
                                    if (existingLine) {
                                        // If a line with the same barcode already exists, update its quantity
                                        existingLine.set_quantity(existingLine.quantity + 1);
                                    } else {
                                        // If no line with the same barcode exists, add the product to the order
                                        order.add_product(product);
                                    }
                                }

                                // Update the last scanned barcode
                                order.same_barcode_product = product.barcode;




                        }



                }
                else{
                   await super._clickProduct(event);
                }
            }
        };
    Registries.Component.extend(ProductScreen, PosProductScreen);
});
