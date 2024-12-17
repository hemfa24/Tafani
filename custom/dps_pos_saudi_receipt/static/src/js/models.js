odoo.define("dps_pos_saudi_receipt.models", function (require) {
"use strict";

	const Registries = require("point_of_sale.Registries");
	const { Order,Orderline } = require('point_of_sale.models');

	const OrderlineExtend = (Orderline) => class OrderlineExtend extends Orderline {
		
		convert_into_float(amount){
			if (amount){
				return parseFloat(amount)
			}
		}
	}
	
	const OrderReceiptModel = (Order) => class OrderReceiptModel extends Order {
		constructor(obj, options) {
			super(...arguments);
			this.order_barcode = this.order_barcode || " ";
			this.set_order_barcode();
		}
		export_as_JSON() {
			const json = super.export_as_JSON(...arguments);
			json.order_barcode = this.order_barcode;
			return json;
		}
		init_from_JSON(json){
			super.init_from_JSON(...arguments);
			this.order_barcode = json.order_barcode || 1;
		}
		get_order_barcode(){
			return this.order_barcode;
		}
		export_for_printing() {
			const json = super.export_for_printing(...arguments);
			json.order_barcode = this.get_order_barcode() || false;
			return json;
		}
		set_order_barcode() {
			this.order_barcode = Math.floor(100000000000 + Math.random() * 9000000000000);
		}
	}

	Registries.Model.extend(Orderline, OrderlineExtend);
	Registries.Model.extend(Order, OrderReceiptModel);


})

