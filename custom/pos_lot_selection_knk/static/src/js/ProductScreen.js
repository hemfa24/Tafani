odoo.define('pos_lot_selection_knk.ProductScreen', function(require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    const BagasonProductScreen = ProductScreen =>
        class extends ProductScreen {
            setup() {
                super.setup();
                
            }
            async _getAddProductOptions(product, base_code) {
                
                let price_extra = 0.0;
                let draftPackLotLines, weight, description, packLotLinesToEdit;

                if (_.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
                    let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
                        .filter((attr) => attr !== undefined);
                    let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
                        product: product,
                        attributes: attributes,
                    });

                    if (confirmed) {
                        description = payload.selected_attributes.join(', ');
                        price_extra += payload.price_extra;
                    } else {
                        return;
                    }
                }

                console.log('call popup ', product.tracking)
                // Gather lot information if required.
                if (['serial', 'lot'].includes(product.tracking) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    console.log('>>>>>>')
                    const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
                    if (isAllowOnlyOneLot) {
                        packLotLinesToEdit = [];
                    } else {
                        const orderline = this.currentOrder
                            .get_orderlines()
                            .filter(line => !line.get_discount())
                            .find(line => line.product.id === product.id);
                        if (orderline) {
                            packLotLinesToEdit = orderline.getPackLotLinesToEdit();
                        } else {
                            packLotLinesToEdit = [];
                        }
                    }
                    var product_quants = [];
                    var { quants, lots }  = await this.fetchLotDetails();
                    if (quants && product) {
                        quants.forEach(function(quant) {
                            if (quant.product_id[0] === product.id && quant.available_quantity > 0) {
                                product_quants.push(quant)
                            }
                        })
                    }
                    var product_lots = [];
                    if (lots && product) {
                        lots.forEach(function(lot) {
                            if (lot.product_id[0] === product.id) {
                                var quant = product_quants.filter(quant => quant.lot_id[0] === lot.id)[0]
                                var quantity = 0;
                                if(quant){
                                    quantity = quant.available_quantity
                                }
                                lot.quantity = quantity
                                product_lots.push(lot)
                            }
                        })
                    }
                    var tracking = ''
                    if (product && product.tracking){
                        tracking = product.tracking
                    }
                    
                    if (product.qty_available > 0){
                        const { confirmed, payload } = await this.showPopup('EditListPopup', {
                            title: this.env._t('Lot/Serial Number(s) Required'),
                            isSingleItem: isAllowOnlyOneLot,
                            array: packLotLinesToEdit,
                            product: product,
                            product_quants: product_quants,
                            product_lots: product_lots,
                            tracking: tracking,


                        });
                        if (confirmed) {
                        
                            console.log('call comfirm ')
                            // Segregate the old and new packlot lines
                            const modifiedPackLotLines = Object.fromEntries(
                                payload.newArray.filter(item => item.id).map(item => [item.id, item.text, item.qty])
                                );
                                const newPackLotLines = payload.newArray
                                .filter(item => !item.id)
                                .map(item => ({ lot_name: item.text, qty: item.qty }));
                                
                                draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
                                console.log('call after  comfirm '), draftPackLotLines
                        } else {
                            // We don't proceed on adding product.
                            return;
                        }

                    }
                    else{
                        return;

                    }
                }

                // Take the weight if necessary.
                if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
                    // Show the ScaleScreen to weigh the product.
                    if (this.isScaleAvailable) {
                        const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
                            product,
                        });
                        if (confirmed) {
                            weight = payload.weight;
                        } else {
                            // do not add the product;
                            return;
                        }
                    } else {
                        await this._onScaleNotAvailable();
                    }
                }

                if (base_code && this.env.pos.db.product_packaging_by_barcode[base_code.code]) {
                    weight = this.env.pos.db.product_packaging_by_barcode[base_code.code].qty;
                }

                let res = { draftPackLotLines, quantity: weight, description, price_extra };
                res.barcode = base_code.base_code;
                return res;
            }
            async _updateSelectedOrderline(event) {
            
                super._updateSelectedOrderline(event);
                if (this.env.pos.numpadMode === 'quantity') {
                    let order = this.env.pos.get_order();
                    let selectedLine = order.get_selected_orderline();
                    if (selectedLine) {
                        if (selectedLine.has_product_lot) {
                            if (selectedLine.pack_lot_lines.length > 0) {
                                let lot_name = selectedLine.pack_lot_lines[0].lot_name
                                let lot_details = await this.fetchLotDetails(selectedLine.product.id, lot_name);
                                let quant = lot_details.quants
                                if (quant && event.detail.key != 'Backspace'){
                                    if (selectedLine.quantity > quant[0].available_quantity) {
                                        selectedLine.set_quantity(quant[0].available_quantity);
                                        return Gui.showPopup("ErrorPopup", {
                                            'title': _t("Invalid Product Qty"),
                                            'body': _.str.sprintf(_t('The '+ quant[0].lot_id[1] + ' lot for product ' + quant[0].product_id[1] + ' has only ' + quant[0].available_quantity + ' qty.')),
                                        });
                                    }

                                }else if (quant && event.detail.key == 'Backspace'){
                                    if (selectedLine.quantity > quant[0].available_quantity) {
                                        selectedLine.set_quantity(quant[0].available_quantity);
                                    }

                                }else{
                                    return;
                                }
                            }
                        }
                    }
                }
            }
            async fetchLotDetails(product=false, lot_name=false) {
                
                var location = this.env.pos.config.default_location_src_id
                var domain = [['available_quantity', '>', 0]]
                if (product){
                    domain.push(['product_id', '=', parseInt(product)])
                }
                if (lot_name){
                    domain.push(['lot_id.name', '=', lot_name])
                }
                if (location){
                    domain.push('|', ['location_id', '=', false], ['location_id', 'child_of', [location[0]]])
                }
                var quants = await this.rpc({
                    model: 'stock.quant',
                    method: 'search_read',
                    domain: domain,
                    fields: ['id', 'lot_id', 'company_id', 'product_id', 'available_quantity'],
                });
                var lot_domain = [['product_qty', '>', 0]]
                if (product){
                    lot_domain.push(['product_id', '=', parseInt(product)])
                }
                if(quants && quants.map(function(quant){return quant.lot_id[0]}).filter(item => item != undefined).length > 0){
                    lot_domain.push(['id', 'in', quants.map(function(quant){return quant.lot_id[0]}).filter(item => item != undefined)])
                }
                var lots = await this.rpc({
                    model: 'stock.lot',
                    method: 'search_read',
                    domain: lot_domain,
                    fields: ['id', 'name', 'product_id', 'expiration_date', 'removal_date', 'use_date'],
                });
                return { quants, lots };
            }

        };

    Registries.Component.extend(ProductScreen, BagasonProductScreen);

    return ProductScreen;
});