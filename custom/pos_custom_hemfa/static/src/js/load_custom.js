/**@odoo-module */
import { PosGlobalState } from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';
var models = require('point_of_sale.models');
var PosDB = require('point_of_sale.DB');

PosDB.include({
    init: function (options) {
        var self = this;
        this._super(options);

    },
    _product_search_string: function (product) {
        var str = product.display_name;
        if (product.barcode) {
            str += '|' + product.barcode;
        }
        if (product.default_code) {
            str += '|' + product.default_code;
        }
        if (product.description) {
            str += '|' + product.description;
        }
        if (product.description_sale) {
            str += '|' + product.description_sale;
        }
        var self = this;
        if (product.pos_multi_barcode_option.length > 0) {

            for (var j = 0; j < product.pos_multi_barcode_option.length; j++) {

                if (product.pos_multi_barcode_option[j].name) {
                    var posbarcode = product.pos_multi_barcode_option[j].name;
                    if (posbarcode) {
                        str += '|' + posbarcode;
                    }
                }
            }

        }
        str = product.id + ':' + str.replace(/:/g, '') + '\n';
        return str

    },
    add_products: function (products) {
        var self = this;
        this._super(products);

        for (var i = 0, len = products.length; i < len; i++) {
            var product = products[i];
            if (product.pos_multi_barcode_option) {
                for (var j = 0; j < product.pos_multi_barcode_option.length; j++) {
                    this.product_by_barcode[product.pos_multi_barcode_option[j].name] = product;
                }
            }
        }




    },


});




Registries.Model.extend(PosGlobalState, barcode_custom)