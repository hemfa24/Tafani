odoo.define("sh_pos_all_in_one_retail.sh_pos_all_in_one_retrai.models", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const { PosGlobalState } = require('point_of_sale.models');

    const shProductPosGlobalState = (PosGlobalState) => class shProductPosGlobalState extends PosGlobalState {

        async _processData(loadedData) {
            await super._processData(...arguments);
            this.product_categories_data = loadedData['product.category'] || [];
            this.pos_category = loadedData['pos.category'] || [];
        }
        
    }

    Registries.Model.extend(PosGlobalState, shProductPosGlobalState);

});