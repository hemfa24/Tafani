odoo.define("sh_pos_secondary.ChangeUOMButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");

    class ChangeUOMButton extends PosComponent {
        setup() {
            super.setup()
            useListener("click", this.onClickUOM);
        }
        add_class(event){
        }
        async onClickUOM() {
            var self = this;
            var selectionList = [];
            var line = this.env.pos.get_order().get_selected_orderline();
            if(this.env.pos.config.sh_enable_multi_barcode && line && this.env.pos.get_order().get_selected_orderline().product.barcode_line_ids.length){
                var selectionList = []
                var barcode_line_ids = this.env.pos.get_order().get_selected_orderline().product.barcode_line_ids
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
            const { confirmed, payload: selectedUOM } = await this.showPopup("SelectionPopup", {
                title: this.env._t("Select the UOM"),
                list: selectionList,
            });

            if (confirmed) {
                if(this.env.pos.config.sh_enable_multi_barcode && line){
                    let product = selectedUOM
                    var pricelist = self.env.pos.db.pricelist_by_id[selectedUOM.price_lst]
                    if(pricelist && product.price_lst){
                        // var price = this.props.product.get_price(pricelist, 1, 0)
                        var price = 0;
                        var quantity = 1;
                        var date = moment();
                        _.find(pricelist.item_ids, function (item_id) {
                            let rule = self.env.pos.db.pricelist_item_by_id[item_id]
                            var productObj = self.env.pos.db.get_product_by_id(product.product_id)

                            if (((productObj.id == rule.product_id) || productObj.product_tmpl_id == rule.product_tmpl_id[0]) &&product.unit == rule.uom_id[0] && ((!rule.categ_id || _.contains(self.parent_category_ids.concat(self.categ.id), rule.categ_id[0])) &&
                                (!rule.date_start || moment.utc(rule.date_start).isSameOrBefore(date)) &&
                                (!rule.date_end || moment.utc(rule.date_end).isSameOrAfter(date))
                            )){
                                if (rule.min_quantity && quantity < rule.min_quantity) {
                                    return false;
                                }
                                if (rule.base === 'pricelist') {
                                    let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                                        return pricelist.id === rule.base_pricelist_id[0];});
                                    if (base_pricelist) {
                                        price = self.get_price(base_pricelist, quantity);
                                    }
                                } else if (rule.base === 'standard_price') {
                                    price = self.standard_price;
                                }

                                if (rule.compute_price === 'fixed') {
                                    price = rule.fixed_price;
                                    return true;
                                } else if (rule.compute_price === 'percentage') {
                                    price = price - (price * (rule.percent_price / 100));
                                    return true;
                                } else {
                                    var price_limit = price;
                                    price = price - (price * (rule.price_discount / 100));
                                    if (rule.price_round) {
                                        price = round_pr(price, rule.price_round);
                                    }
                                    if (rule.price_surcharge) {
                                        price += rule.price_surcharge;
                                    }
                                    if (rule.price_min_margin) {
                                        price = Math.max(price, price_limit + rule.price_min_margin);
                                    }
                                    if (rule.price_max_margin) {
                                        price = Math.min(price, price_limit + rule.price_max_margin);
                                    }
                                }
                            }
                        })
                        let secondaryUom = self.env.pos.units_by_id[selectedUOM.unit]
                        if (secondaryUom){
                            let converted_price  = price / secondaryUom.ratio

                            if (converted_price){
                                line.set_unit_price(converted_price)
                                line.price_manually_set = true
                                line.change_current_uom(secondaryUom);
                            }
                        }
                    } else{
                        line.price_manually_set = true
                        await line.set_unit_price(selectedUOM.price)
                        if (selectedUOM && selectedUOM.unit){
                            let unit = self.env.pos.units_by_id[selectedUOM.unit]
                            line.change_current_uom(unit);
                        }
                    }
                }else{
                    line.change_current_uom(selectedUOM);
                }

            }
        }
    }
    ChangeUOMButton.template = "ChangeUOMButton";

    ProductScreen.addControlButton({
        component: ChangeUOMButton,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(ChangeUOMButton);

    return ChangeUOMButton;
});
