odoo.define('pos_lot_selection_knk.model_load', function(require) {
    "use strict";

    var { PosGlobalState, Order, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    
    const NewPosGlobalState = (PosGlobalState) => class NewPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.stock_lot = loadedData['stock.lot'];            
        }

        
    }
    Registries.Model.extend(PosGlobalState, NewPosGlobalState);

    const StockLocation = (Order) => class StockLocation extends Order {
    constructor() {
        super(...arguments);
        
    }
    add_product(product, options) { 
        var res = super.add_product(...arguments);           
        var self = this;
        if (options.draftPackLotLines) {
            self.selected_orderline.setPackLotLines(options.draftPackLotLines);
            var qties = 1;
            if(product.tracking != 'serial'){

                if (options.draftPackLotLines.newPackLotLines){
                
                    
                    var qties = options.draftPackLotLines.newPackLotLines.map(function(line){
                        return line.qty
                    });
                    if(qties.length > 0){
                        qties.reduce(function(a, b){return a + b});
                    }
                }
                self.selected_orderline.set_quantity(qties)
            }
        }
        return res
    }
    
    }
    Registries.Model.extend(Order, StockLocation);

});