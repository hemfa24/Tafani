odoo.define('pos_lot_selection_knk.OrderWidget', function(require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    const OrderWidget = require('point_of_sale.OrderWidget'); 
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    
    const BagasonOrderWidget = OrderWidget =>
        class extends OrderWidget {
            setup() {
                super.setup();
                
            }
            async _editPackLotLines(event) {
                
                const orderline = event.detail.orderline;
                const product = orderline.product;
                const isAllowOnlyOneLot = orderline.product.isAllowOnlyOneLot();
                const packLotLinesToEdit = orderline.getPackLotLinesToEdit(isAllowOnlyOneLot);
                var product_quants = [];
                var { quants, lots } = await this.fetchLotDetails();
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
                            lot.quantity = quant.available_quantity
                            product_lots.push(lot)
                        }
                    })
                }
                var tracking = ''
                if (product && product.tracking){
                    tracking = product.tracking
                }
                const { confirmed, payload } = await this.showPopup('EditListPopup', {
                        title: this.env._t('Lot/Serial Number(s) Required'),
                        isSingleItem: isAllowOnlyOneLot,
                        array: packLotLinesToEdit,
                        product: orderline.product,
                        product_quants: product_quants,
                        product_lots: product_lots,
                        tracking: tracking,
                        product_qty: tracking === 'lot' ? orderline.get_quantity() : undefined,
                        existing: true,

                });
                if (confirmed) {
                    // Segregate the old and new packlot lines
                    const modifiedPackLotLines = Object.fromEntries(
                        payload.newArray.filter(item => item.id).map(item => [item.id, item.text, item.qty])
                    );
                    const newPackLotLines = payload.newArray
                        .filter(item => !item.id)
                        .map(item => ({ lot_name: item.text, qty: item.qty }));
                    orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
                    var qties = 0;
                    if(orderline.product.tracking === 'lot'){
                        if (newPackLotLines.length > 0){
                            qties += newPackLotLines.map(function(line){
                                    if(line.qty != undefined){
                                        return line.qty
                                    }
                                }).reduce(function(a, b){return a + b});
                        }
                        if(payload.newArray.filter(item => item.id).length > 0){
                            qties += payload.newArray.filter(item => item.id).map(function(line){
                                if(line.qty != undefined){
                                    return line.qty}
                                }).reduce(function(a, b){return a + b});
                        }
                        orderline.set_quantity(qties)
                    }
                }
                this.order.select_orderline(event.detail.orderline);
            }
            async fetchLotDetails() {
                var location = this.env.pos.config.default_location_src_id
                var domain = [['quantity', '>', 0]]
                if (location){
                    domain.push('|', ['location_id', '=', false], ['location_id', 'child_of', [location[0]]])
                }
                var quants = await this.rpc({
                    model: 'stock.quant',
                    method: 'search_read',
                    orderBy: [{name: 'create_date', asc: true}],
                    domain: domain,
                    fields: ['id', 'lot_id', 'company_id', 'product_id', 'available_quantity'],
                });
                var lot_domain = [['product_qty', '>', 0]]
                if(quants && quants.map(function(quant){return quant.lot_id[0]}).filter(item => item != undefined).length > 0){
                    lot_domain.push(['id', 'in', quants.map(function(quant){return quant.lot_id[0]})])
                }
                var lots = await this.rpc({
                    model: 'stock.lot',
                    method: 'search_read',
                    domain: lot_domain,
                    orderBy: [{name: 'create_date', asc: true}, {name: 'expiration_date', asc: true}],
                    fields: ['id', 'name', 'product_id', 'expiration_date', 'removal_date', 'use_date'],
                });
                return { quants, lots };
            }
        };

    Registries.Component.extend(OrderWidget, BagasonOrderWidget);

    return OrderWidget;
});
