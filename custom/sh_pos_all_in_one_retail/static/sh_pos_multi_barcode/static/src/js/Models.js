odoo.define("sh_pos_multi_barcode.models", function (require) {
    "use strict";

    const { PosGlobalState, Orderline, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const shPosmultibarcodePoModel = (PosGlobalState) => class shPosmultibarcodePoModel extends PosGlobalState {
        async _processData(loadedData) {
            var self = this
            self.db.product_by_barcode = {}
            self.db.multi_barcode_by_id = loadedData['product_by_barcode'] || {}
            self.db.barcode_by_name = loadedData['barcode_by_name'] || {}
            await super._processData(...arguments)
        }

        async _loadProductProduct(products) {
            await super._loadProductProduct(products)
            var self = this;
            if (self.config.sh_enable_multi_barcode){

                _.each(self.db.multi_barcode_by_id,async function (barcode) {
                    if (barcode.product_id){
                        var product = await self.db.product_by_id[barcode.product_id[0]]
                        if (product){
                            self.db.product_by_barcode[barcode.name] = product
                            if (self.db.product_by_barcode[barcode.name]){

                                if(self.db.product_by_id[barcode.product_id[0]]['multi_barcodes']){
                                    self.db.product_by_id[barcode.product_id[0]]['multi_barcodes'] += '|' + barcode.name
                                }else{
                                    self.db.product_by_id[barcode.product_id[0]]['multi_barcodes'] = barcode.name
                                }
                            }
                        }
                    }
                })


            }
        }

    }
    Registries.Model.extend(PosGlobalState, shPosmultibarcodePoModel);

//    const ShPosMultiBarcodeorderline = (Orderline) => class ShPosMultiBarcodeorderline extends Orderline {
//        async set_quantity(quantity, keep_price) {
//            var self = this;
//            if (self.pos.config.sh_enable_multi_barcode && this && this.get_product() && this.get_product().is_add_using_barcode && !this.negative_qty_price){
//                if(quantity <= 0){
//                    alert("Not allow negative quantity !2")
//                    return false
//                }
//            }
//            return super.set_quantity(quantity, keep_price)
//        }
//        set_unit_price(price) {
//            var self = this;
//            if (self.pos.config.sh_enable_multi_barcode && this && this.get_product() && this.get_product().is_add_using_barcode && !this.negative_qty_price){
//                if(price < 0.1){
//                    alert("Not allow negative price !1")
//                    return false
//                }
//            }
//            return super.set_unit_price(price)
//        }
//    }
//    Registries.Model.extend(Orderline, ShPosMultiBarcodeorderline);

//    const ShPosMultiBarcodeOrder = (Order) => class ShPosMultiBarcodeOrder extends Order {
//        async add_product(product, options) {
//            await super.add_product(...arguments);
//            var self = this;
//            if(this.pos.config.sh_enable_multi_barcode && $('.products-widget-control .search-bar-container .pos-search-bar input') && $('.products-widget-control .search-bar-container .pos-search-bar input').val()){
//                var barcode = this.pos.db.barcode_by_name[$('.products-widget-control .search-bar-container .pos-search-bar input').val()]
//                if(barcode){
//                    if(this.pos.db.product_by_barcode[barcode.name]){
// //                        if{
// //                            if(this.pos.get_order().get_selected_orderline() && barcode.price && !barcode.price_lst){
//                            if(this.pos.get_order().get_selected_orderline() && barcode.price && barcode.price_lst){
//                                this.pos.get_order().get_selected_orderline().set_unit_price(barcode.price)
//                                this.pos.get_order().get_selected_orderline().price = barcode.price
//                                this.pos.get_order().get_selected_orderline().price_manually_set = true

//                                this.pos.get_order().get_selected_orderline()['negative_qty_price'] = barcode.negative_qty_price
//                                this.pos.get_order().get_selected_orderline().get_product()['is_add_using_barcode'] = true
//                            }
//                            if(this.get_selected_orderline() && barcode.unit){
//                                var units = ''
//                                if(barcode.unit[0]){
//                                    units = this.pos.units_by_id[barcode.unit[0]]
//                                }else{
//                                    units = this.pos.units_by_id[barcode.unit]
//                                }
//                                if(units){
//                                    this.get_selected_orderline().change_current_uom(units);
//                                }
//                            }
//                            if(this.get_selected_orderline() && barcode.price && barcode.price_lst){
//                                var pricelist = ''
//                                if(barcode.price_lst[0]){
//                                    pricelist = this.pos.db.pricelist_by_id[barcode.price_lst[0]]
//                                }else{
//                                    pricelist = this.pos.db.pricelist_by_id[barcode.price_lst]
//                                }
//                                if(pricelist){
//                                    // var price = this.pos.get_order().get_selected_orderline().product.get_price(pricelist, this.pos.get_order().get_selected_orderline().get_quantity(), this.pos.get_order().get_selected_orderline().get_price_extra())
//                                    let productSearched = this.pos.db.barcode_by_name[this.pos.product_search]

//                                    var price = 0;
//                                    var quantity = this.get_selected_orderline().quantity;
//                                    var date = moment();
//                                    _.find(pricelist.item_ids, function (item_id) {
//                                        let rule = self.pos.db.pricelist_item_by_id[item_id['id']]
//                                        var productObj = self.pos.db.get_product_by_id(productSearched.product_id)
//                                        if (rule && productObj) {
//                                            if (((productObj.id == rule.product_id[0]) || productObj.product_tmpl_id == rule.product_tmpl_id) &&productSearched.unit == rule.uom_id && (
//                                                (!rule.categ_id || _.contains(self.parent_category_ids.concat(self.categ.id), rule.categ_id[0])) &&
//                                                (!rule.date_start || moment.utc(rule.date_start).isSameOrBefore(date)) &&
//                                                (!rule.date_end || moment.utc(rule.date_end).isSameOrAfter(date))
//                                            )){

//                                                if (rule.min_quantity && quantity < rule.min_quantity) {
//                                                    console.log()
//                                                    return false;
//                                                }
//                                                if (rule.base === 'pricelist') {
//                                                    let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
//                                                        return pricelist.id === rule.base_pricelist_id[0];});
//                                                    if (base_pricelist) {
//                                                        price = self.get_price(base_pricelist, quantity);
//                                                    }
//                                                } else if (rule.base === 'standard_price') {
//                                                    price = self.standard_price;
//                                                }

//                                                if (rule.compute_price === 'fixed') {
//                                                    price = rule.fixed_price;
//                                                    return true;
//                                                } else if (rule.compute_price === 'percentage') {
//                                                    price = price - (price * (rule.percent_price / 100));
//                                                    return true;
//                                                } else {
//                                                    var price_limit = price;
//                                                    price = price - (price * (rule.price_discount / 100));
//                                                    if (rule.price_round) {
//                                                        price = round_pr(price, rule.price_round);
//                                                    }
//                                                    if (rule.price_surcharge) {
//                                                        price += rule.price_surcharge;
//                                                    }
//                                                    if (rule.price_min_margin) {
//                                                        price = Math.max(price, price_limit + rule.price_min_margin);
//                                                    }
//                                                    if (rule.price_max_margin) {
//                                                        price = Math.min(price, price_limit + rule.price_max_margin);
//                                                    }
//                                                }
//                                            }
//                                        }
//                                    })

//                                    let secondaryUom = this.pos.units_by_id[productSearched.unit]
//                                    if (secondaryUom){
//                                        let converted_price  = price / secondaryUom.ratio
//                                        if (converted_price){
//                                            this.pos.get_order().get_selected_orderline().set_unit_price( converted_price );
//                                            this.pos.get_order().get_selected_orderline().price_manually_set = true
//                                            this.pos.get_order().get_selected_orderline()['negative_qty_price'] = barcode.negative_qty_price
//                                            this.pos.get_order().get_selected_orderline().get_product()['is_add_using_barcode'] = true
//                                        }else{
//                                            alert('Item not found in pricelist !')
//                                            this.pos.get_order().remove_orderline(this.pos.get_order().get_selected_orderline())
//                                        }
//                                    }

//                                    // this.pos.get_order().get_selected_orderline().set_unit_price(this.pos.get_order().get_selected_orderline().product.get_price(pricelist, this.pos.get_order().get_selected_orderline().get_quantity(), this.pos.get_order().
//                                    // get_selected_orderline().get_price_extra()));

//                                }
//                            }

// //                        }
//                    }
//                }
//            }
//        }
//    };
//    Registries.Model.extend(Order, ShPosMultiBarcodeOrder);

});
