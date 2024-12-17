odoo.define("sh_pos_advance_cache.cache_product", function (require) {
    "use strict";

    var indexedDB = require('sh_pos_advance_cache.indexedDB');
    const { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const rpc = require("web.rpc");

    const shPosProductModel = (PosGlobalState) => class shPosProductModel extends PosGlobalState {
        send_current_order_to_customer_facing_display() {
            var self = this;
            if (this.config && !this.config.iface_customer_facing_display) return;
            if (this.config && this.config.iface_customer_facing_display) {
                this.render_html_for_customer_facing_display().then((rendered_html) => {
                    if (self.env.pos.customer_display) {
                        var $renderedHtml = $('<div>').html(rendered_html);
                        $(self.env.pos.customer_display.document.body).html($renderedHtml.find('.pos-customer_facing_display'));
                        var orderlines = $(self.env.pos.customer_display.document.body).find('.pos_orderlines_list');
                        orderlines.scrollTop(orderlines.prop("scrollHeight"));
                    } else if (this.config.iface_customer_facing_display_via_proxy && this.env.proxy.posbox_supports_display) {
                        this.env.proxy.update_customer_facing_display(rendered_html);
                    }
                });
            }
        }

        async _processData(loadedData) {
            const productModel = 'product.product'
            if (localStorage.getItem('product.product') === 'loaded') {
                // Remove deleted products from indexed db
                await rpc.query({
                    model: 'product.update',
                    method: 'search_read',
                    args: [[]],
                }).then(async function (result) {
                    if (result) {
                        for (var i = 0; i < result.length; i++) {
                            await indexedDB.get_by_id('product.product', parseInt(result[i]['delete_ids'])).then(function (cache_product) {
                                indexedDB.delete_item('product.product', parseInt(result[i]['delete_ids']))
                            });
                        }
                    }
                });
                //                
                var all_products = []
                await indexedDB.get_all('product.product').then(function (cache_products) {
                    all_products = cache_products
                });
                loadedData['product.product'] = all_products
            } else {
                var all_products = []
                await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'sh_load_model',
                    args: [odoo.pos_session_id, productModel],
                }).then(function (result) {
                    if (result) {
                        all_products = result
                        indexedDB.save_data('product.product', all_products)
                    }
                });

                loadedData['product.product'] = all_products
                localStorage.setItem('product.product', 'loaded')
            }
            await super._processData(...arguments);
        }
    }
    Registries.Model.extend(PosGlobalState, shPosProductModel);

});
