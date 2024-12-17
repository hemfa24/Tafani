odoo.define("sh_pos_secondary.SelectionPopup", function (require) {
    "use strict";

    const SelectionPopup = require("point_of_sale.SelectionPopup");
    const Registries = require('point_of_sale.Registries');

    const ShSelectionPopup = (SelectionPopup) =>
        class extends SelectionPopup {
            setup(){
                super.setup()
            }

           selectItem(itemId) {
           var self = this
           if(this.props.title == "Select the UOM") {
             $(self.props.list).each(function(index, product_list){
                    var this_product = this
                    var uom_product_set = Number(this.item.product_id && this.item.product_id[0])
                    if (!uom_product_set){
                        uom_product_set = Number(this.item.product_id)
                    }
                    var uom = this.unit
                    var ssss = this_product.item
                    if(itemId == this_product.id) {
                        if(self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product === itemId)  ){
                                let ccc =self.env.pos.get_order().get_orderlines().find(line => line.same_barcode_product === itemId);
                                ccc.set_quantity(ccc.quantity+1)

                        }

                        else{
                        if(self.env.pos.get_order().get_selected_orderline() && self.env.pos.get_order().get_selected_orderline().same_barcode_product == itemId){
                             self.env.pos.get_order().get_selected_orderline().set_quantity(self.env.pos.get_order().get_selected_orderline().quantity+1)

                        }
                        else if(self.env.pos.get_order().get_orderlines().find(line => line.barcode_orderline == this_product.label)  ){
                                        let ccc =self.env.pos.get_order().get_orderlines().find(line => line.barcode_orderline === this_product.label);
                                        ccc.set_quantity(ccc.quantity+1)
                        }
                        else{
                                    self.env.pos.get_order().add_product(self.env.pos.db.product_by_id[uom_product_set], {
                                    price: this_product.item.price,
                                    lst_price: this_product.item.price,
//                                    quantity: 10,
                                    extras: {
                                        price_manually_set: true,
                                    },
                                    });
                                    self.env.pos.get_order().get_selected_orderline().same_barcode_product = itemId
                                     var secondaryUom;
                                    if (ssss.unit && ssss.unit[0]){
                                        secondaryUom = self.env.pos.units_by_id[ssss.unit[0]]
                                    }else{
                                        secondaryUom = self.env.pos.units_by_id[ssss.unit]
                                    }
                                    self.env.pos.get_order().get_selected_orderline().change_current_uom(secondaryUom);
                                    self.env.pos.get_order().get_selected_orderline().barcode_add = this_product.label;
                                    self.env.pos.get_order().get_selected_orderline().negative_qty_price = ssss.negative_qty_price;
                                    self.env.pos.get_order().orderlines.negative_qty_price = ssss.negative_qty_price;
                        }


                        }


//                            line





                    }


            })

           }
           else{
            self.state.selectedId = itemId;
            self.confirm();
           }
          }

          add_class(event){
                let clicked_row = Number(this.item.product_id)
                if($(clicked_row).hasClass("highlight")){
                    $(clicked_row).removeClass()
                }
                else{
                    $(clicked_row).addClass("highlight")
                }
            }
        }

    Registries.Component.extend(SelectionPopup, ShSelectionPopup)

});
