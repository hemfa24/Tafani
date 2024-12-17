odoo.define('dps_pos_saudi_receipt.maiOrderReceipt', function(require) {
	"use strict";

	const OrderReceipt = require('point_of_sale.OrderReceipt');
	const Registries = require('point_of_sale.Registries');

	const maiOrderReceipt = OrderReceipt => 
		class extends OrderReceipt {
			constructor() {
				super(...arguments);
			}

			get order_barcode() {
				console.log('----------------------',this);
				let order = this.env.pos.get_order();
				let barcode = order.order_barcode.toString();
				if($('#order_barcode').length > 0){
					JsBarcode("#order_barcode", barcode);
				}
				return false;
			}
	};

	Registries.Component.extend(OrderReceipt, maiOrderReceipt);
	return OrderReceipt;
});