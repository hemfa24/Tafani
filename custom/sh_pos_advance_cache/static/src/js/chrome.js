odoo.define("sh_pos_advance_cache.chrome", function (require) {
	"use strict";

	const Registries = require("point_of_sale.Registries");
	const Chrome = require("point_of_sale.Chrome");
	const ProductItem = require("point_of_sale.ProductItem");
	var indexedDB = require('sh_pos_advance_cache.indexedDB');
	var utils = require('web.utils');

	const PosResChrome = (Chrome) =>
		class extends Chrome {
			async _buildChrome() {
				super._buildChrome();
				var self = this;
				this.env.services['bus_service'].addEventListener('notification', async ({ detail: notifications }) => {
					for (var notif of notifications) {
						if (notif.type == 'product_update') {
							if (notif.payload && notif.payload[0]) {
								notif.payload[0]['display_name'] = notif.payload[0]['name']
								indexedDB.save_data('product.product', [notif.payload[0]])
								var product_obj = self.env.pos.db.product_by_id[notif.payload[0].id]
								if (self && self.env && self.env.pos) {
									if (self.env.pos.config.sh_product_upate == 'online') {
										$.extend(product_obj, notif.payload[0]);
										await self.env.pos._addProducts([notif.payload[0].id], false);

										if (self && self.env && self.env.pos && self.env.pos.db && self.env.pos.config && self.env.pos.config.sh_enable_multi_barcode) {
											self.env.pos.db.product_by_barcode = {}
											_.each(self.env.pos.db.multi_barcode_by_id,await function (barcode) {
												if (barcode.product_id){
													var product = self.env.pos.db.product_by_id[barcode.product_id]
													if (product){
														self.env.pos.db.product_by_barcode[barcode.name] = product
														if (self.env.pos.db.product_by_barcode[barcode.name]){

															if(self.env.pos.db.product_by_id[barcode.product_id]['multi_barcodes']){
																self.env.pos.db.product_by_id[barcode.product_id]['multi_barcodes'] += '|' + barcode.name
															}else{
																self.env.pos.db.product_by_id[barcode.product_id]['multi_barcodes'] = barcode.name
															}
														}
													}
												}
											})
											var temp_Str = ""
											if (self.env.pos.db.product_by_barcode){
												await _.each(self.env.pos.db.product_by_barcode, function (each) {
													var search_barcode = utils.unaccent(self.env.pos.db.barcode_product_search_string(each))
													temp_Str += search_barcode
												})
											}
											self.env.pos.db.barcode_search_str = temp_Str
										}
									}
								}
							}
						}
						if (notif.type == 'customer_update') {
							if (notif.payload && notif.payload[0]) {
								indexedDB.save_data('res.partner', [notif.payload[0]])
								var partner_obj = self.env.pos.db.partner_by_id[notif.payload[0].id]
								if (self && self.env && self.env.pos) {
									if (self.env.pos.config.sh_partner_upate == 'online') {
										$.extend(partner_obj, notif.payload[0]);
										self.env.pos._loadPartners([notif.payload[0].id]);
									}
								}

							}
						}
						if (notif.type == 'product_barcode_update') {
							if(notif.payload){
								if (self && self.env && self.env.pos && self.env.pos.db && self.env.pos.config && self.env.pos.config.sh_enable_multi_barcode && self.env.pos.config.sh_product_upate == 'online') {
									self.env.pos.db.multi_barcode_by_id = {}
									self.env.pos.db.multi_barcode_by_id = notif.payload
									_.each(notif.payload, function(each){
										self.env.pos.db.barcode_by_name[each.name] = each
										if(each.product_id && self.env.pos.db.get_product_by_id(each.product_id)){
											self.env.pos.db.get_product_by_id(each.product_id).multi_barcodes = ""
										}
									});
								}
							}
						}
						if (notif.type == 'product_barcode_delete') {
							if(notif.payload && self.env && self.env.pos && self.env.pos.db && self.env.pos.db.multi_barcode_by_id && self.env.pos.db.multi_barcode_by_id[notif.payload]){
								for (let each of notif.payload){
                                    delete self.env.pos.db.multi_barcode_by_id[each.id];
								}
							}
						}
						if (notif.type == 'product_suggestion_update') {
							if(notif.payload && self.env && self.env.pos && self.env.pos.config.enable_product_suggestion && self.env.pos.suggestions){
								self.env.pos.suggestion = {}
								self.env.pos.suggestion = notif.payload
							}
						}
						if (notif.type == 'product_bundle_update') {
							if(notif.payload && self.env && self.env.pos && self.env.pos.config.enable_product_bundle){
								self.env.pos.db.bundle_by_product_id = {}
								self.env.pos.db.add_bundles(notif.payload);
							}
						}
						if (notif.type == 'product_tag_update') {
							if(notif.payload && self.env && self.env.pos && self.env.pos.config.sh_search_product && notif.payload){
								self.env.pos.db.product_tag_data = []
								self.env.pos.db.product_tag_data = notif.payload
								_.each(self.env.pos.db.product_tag_data,function(each_tag){
									self.env.pos.db.product_by_tag_id[each_tag.id] = each_tag
								})
							}
						}
						if (notif.type == 'product_pricelist') {

							self.env.pos.pricelists = []
							self.env.pos.pricelists = notif.payload
							// self.env.pos.get_order().pricelist.items[0].fixed_price = 56
							_.each(notif.payload, function(each_notif){
								if(each_notif.id == self.env.pos.config.pricelist_id.id || each_notif.id == self.env.pos.config.pricelist_id[0]){
									self.env.pos.default_pricelist = each_notif
									self.env.pos.get_order().set_pricelist(each_notif)
								}
								_.each(each_notif.items, function(each_item){
									_.each(self.env.pos.get_order().pricelist.items, function(each_order_item){
										if(each_item.id == each_order_item.id){
											each_order_item.fixed_price = each_item.fixed_price
										}
									});
								});
							})
						}
						if (notif.type == 'product_pricelist_item_update') {
							if(notif.payload && notif.payload.length > 0){


								_.each(notif.payload, await function(each_notif){
									// self.env.pos.get_order().pricelist.items = []
									self.env.pos.db.pricelist_item_by_id[each_notif.id] = each_notif
									if (self.env.pos.db.pricelist_by_id[each_notif.pricelist_id[0]]){
										var pricelist = self.env.pos.db.pricelist_by_id[each_notif.pricelist_id[0]]
										if (!pricelist.item_ids.includes(each_notif.id)){
											pricelist.item_ids.push(each_notif.id)
										}
									}
									// self.env.pos.get_order().pricelist.items.push(each_notif)
									if(each_notif.product_id){
										var products = self.env.pos.db.get_product_by_id(each_notif.product_id[0])
										if(products && products.applicablePricelistItems){
											products.applicablePricelistItems[each_notif.pricelist_id[0]] = [];
											products.applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif)
										}
									}else if(each_notif.product_tmpl_id){
										var products = Object.values(self.env.pos.db.product_by_id).filter((product1) =>  product1.product_tmpl_id == each_notif.product_tmpl_id[0] && product1.active )
										if(products && products[0] && products[0].applicablePricelistItems){
											products[0].applicablePricelistItems[each_notif.pricelist_id[0]] = [];
											// products[0].applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif)
										}

									}else{
										if(self.env.pos.db.product_by_id){
											_.each(self.env.pos.db.product_by_id, function(each_product){
												each_product.applicablePricelistItems[each_notif.pricelist_id[0]] = [];
												// if (!(each_notif.pricelist_id[0] in each_product.applicablePricelistItems)) {
												// 	each_product.applicablePricelistItems[each_notif.pricelist_id[0]] = [];
												// }
												// each_product.applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif);

											});
										}
									}
								});



								_.each(notif.payload, function(each_notif){
									// self.env.pos.get_order().pricelist.items = []
									// self.env.pos.get_order().pricelist.items.push(each_notif)
									if(each_notif.product_id){
										var products = self.env.pos.db.get_product_by_id(each_notif.product_id[0])
										if(products && products.applicablePricelistItems){
											// products.applicablePricelistItems[each_notif.pricelist_id[0]] = [];
											products.applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif)
										}
									}else if(each_notif.product_tmpl_id){
										var products = Object.values(self.env.pos.db.product_by_id).filter((product1) =>  product1.product_tmpl_id == each_notif.product_tmpl_id[0] && product1.active )
										if(products && products[0] && products[0].applicablePricelistItems){
											// products[0].applicablePricelistItems[each_notif.pricelist_id[0]] = [];
											products[0].applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif)
										}

									}else{
										if(self.env.pos.db.product_by_id){
											_.each(self.env.pos.db.product_by_id, function(each_product){
												// each_product.applicablePricelistItems[each_notif.pricelist_id[0]] = [];

												each_product.applicablePricelistItems[each_notif.pricelist_id[0]].push(each_notif);

											});
										}
									}
								});
							}else{
								if(self.env.pos.db.product_by_id){
									_.each(self.env.pos.db.product_by_id, function(each_product){
										// each_product.applicablePricelistItems[each_notif.pricelist_id[0]] = [];

										each_product.applicablePricelistItems = {};

									});
								}
							}
						}
						if (notif.type == 'product_pricelist_item_delete') {
							if(notif.payload){
								for (let each of notif.payload){
									if(each.product_id){
										let item = self.env.pos.db.pricelist_item_by_id[each.id]
										var pricelist = self.env.pos.db.pricelist_by_id[item.pricelist_id[0]]
										if (pricelist){
											var index = pricelist.item_ids.indexOf(each.id)
											pricelist.item_ids.splice(index, 1);
										}
										delete self.env.pos.db.pricelist_item_by_id[each.id];

									}else if(each.product_tmpl_id){
										var products = Object.values(self.env.pos.db.product_by_id).filter((product1) =>  product1.product_tmpl_id == each.product_tmpl_id && product1.active )
										if(products && products[0] && products[0].applicablePricelistItems){

											_.each(products[0].applicablePricelistItems, function(each_product_item){
												if(each.id == each_product_item[0].id){
													delete each_product_item[0]
													// each_product_item[0] = each_notif
													// each_product_item[0].fixed_price = each_notif.fixed_price
												}
											});
										}
										let item = self.env.pos.db.pricelist_item_by_id[each.id]
										var pricelist = self.env.pos.db.pricelist_by_id[item.pricelist_id[0]]
										if (pricelist){
											var index = pricelist.item_ids.indexOf(each.id)
											pricelist.item_ids.splice(index, 1);
										}
										delete self.env.pos.db.pricelist_item_by_id[each.id];
									}
								}
							}
						}
					}
				});
			}
		};
	Registries.Component.extend(Chrome, PosResChrome);

	return Chrome
});
