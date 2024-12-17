odoo.define('pos_lot_selection_knk.ProductLotPopup', function(require) {
    'use strict';

    const { useState} = owl;
    const EditListPopup = require('point_of_sale.EditListPopup');
    const { useAutoFocusToLast } = require('point_of_sale.custom_hooks');
    const { Gui } = require('point_of_sale.Gui');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    

    const ProductLotPopup = (EditListPopup) =>
        class extends EditListPopup {
            setup() { 

                super.setup();
                useListener('add-serial_product', this.addSerialProduct);
                useListener('remove-serial_product', this.RemoveSerialProduct);
                this._id = 0;
                this.state = useState({ array: this._initialize(this.props.array) , default_lot_qty:1});
                useAutoFocusToLast();                
                if (this.props.product_qty > 0){
                    this.state.default_lot_qty = this.props.product_qty
                }
                if(this.state.array.filter(item => !item.id).length > 0){
                    if (this.props.tracking == 'lot'){
                        var quants = this.props.product_quants
                        if (quants.length > 0) {
                            this.state.array[0].text = quants[0].lot_id[1]
                        }
                    }
                }
            }
            _emptyItem() {
                
                var tracking = ''
                var qty = undefined
                if (this.props.tracking){
                    tracking = this.props.tracking
                }
                if(tracking === 'lot'){
                    qty = 1;
                }
                return {
                    text: '',
                    _id: this._nextId(),
                    tracking: tracking,
                    qty: qty,
                };
            }
            _initialize(array) {                                 
                // If no array is provided, we initialize with one empty item.
                if (array.length === 0) return [this._emptyItem()];
                // Put _id for each item. It will serve as unique identifier of each item.
                return array.map((item) => Object.assign({}, { _id: this._nextId() }, typeof item === 'object'? item: { 'text': item}, { tracking:this.props.tracking}, {'qty': this.props.product_qty}));
            }            
            getPayload() { 
                return {
                    newArray: this.state.array
                        .filter((item) => item.text.trim() !== '')
                        .map((item) => Object.assign({qty: item.qty}, item)),
                };
            }
            captureChange(event) {
        
                var quant = this.props.product_quants.filter(item => item.lot_id[0] === parseInt(event.target.value))[0]
                if (quant) {
                    let entered_item_qty = $('.entered_item_qty').find('input');
                    if (quant.lot_id && quant.lot_id[1]) {
                        if (this.props.product.tracking === 'serial'){
                            this.state.array.at(-1).text = quant.lot_id[1]
                        }else{
                            $("input.list-line-input[type='text']").val(quant.lot_id[1]);
                            this.state.default_lot_qty = 1;
                            this.state.array[0].qty = 1
                            this.state.array[0].text = quant.lot_id[1]
                            entered_item_qty.val(1)
                        }
                        $('#qty_limit_warning').css('display', 'none');
                        $('i.decrease_lot_qty').css('opacity', '1');
                        $('i.increase_lot_qty').css('opacity', '1');
                    }
                    this.trigger('keyup');
                } else {
                    this.state.array[0].text = ''
                }
            }
            increaseLotQty(){
                    
                var self = this;
                let entered_item_qty = $('.entered_item_qty').find('input');
                let entered_qty = parseFloat(entered_item_qty.val());
                var lot_name = entered_item_qty.attr('data-lot')
                
                if(lot_name){
                    $('i.decrease_lot_qty').css('opacity', '1');
                    var lot_id = this.props.product_lots.filter(item => item.name == lot_name)[0]
                    if(lot_id && entered_qty >= lot_id.quantity){
                        $('#qty_limit_warning').css('display', 'block');
                        $('i.increase_lot_qty').css('opacity', '0.5');
                    }else if(entered_qty < 0){
                        entered_item_qty.val(0);
                    }else{
                        for (var i=0; i < self.state.array.length; i++) {
                            if (self.state.array[i].text === lot_name) {
                                entered_item_qty.val(entered_qty+1)
                                self.state.array[i].qty = entered_qty+1
                            }
                        }

                    }
                }
            }
            addSerialProduct({detail: serial_name }){

                var self = this;
                let list_of_qty = $('.entered_item_qty');
                $.each(list_of_qty, function(index, value) {
                    if($(value).attr('data-serial') === serial_name){
                        
                        var empty_line = self.state.array.filter(item => !item.text)
                        if(empty_line.length > 0){
                            empty_line[0].text = serial_name;
                        }else{
                            self.state.array.push(
                                {text: serial_name,
                                _id: self._nextId(),
                            });

                        }
                        let remove_button = $(value).find('#remove_serial_product');
                        let add_button = $(value).find('#add_serial_product');
                        remove_button.css('display', 'block');
                        add_button.css('display', 'none');
                    }
                });
            }
            decreaseLotQty(){
                
                var self = this;
                let entered_item_qty = $('.entered_item_qty').find('input');
                let entered_qty = parseFloat(entered_item_qty.val());
                var lot_name = entered_item_qty.attr('data-lot')
                if(entered_qty <= 0){
                    $('i.decrease_lot_qty').css('opacity', '0.5');
                }
                else{
                    for (var i=0; i < self.state.array.length; i++) {
                        if (self.state.array[i].text === lot_name) {
                            entered_item_qty.val(entered_qty-1)
                            self.state.array[i].qty = entered_qty-1
                        }
                    }
                    let new_qty = parseFloat(entered_item_qty.val());
                    if(lot_name && entered_qty > 0){
                        var lot_id = this.props.product_lots.filter(item => item.name == lot_name)[0]
                        if(lot_id && new_qty <= lot_id.quantity){
                            $('#qty_limit_warning').css('display', 'none');
                            $('i.increase_lot_qty').css('opacity', '1');
                        }
                    }

                }

            }
            RemoveSerialProduct({detail: serial_name }){
                var self = this;
                let list_of_qty = $('.entered_item_qty');
                $.each(list_of_qty, function(index, value) {
                    if($(value).attr('data-serial') === serial_name){
                        let remove_button = $(value).find('#remove_serial_product');
                        let add_button = $(value).find('#add_serial_product');
                        remove_button.css('display', 'none');
                        add_button.css('display', 'block');
                        // self.trigger('remove-item', event)
                        let itemToRemove = self.state.array.filter(item => item.text === serial_name);
                    

                        self.state.array.splice(
                            self.state.array.findIndex(item => item._id == itemToRemove[0]._id),
                            1
                        );
                    }
                });
            }
            check_updated_qty(event){
             
                var self = this;
                let entered_qty = parseFloat(event.target.value);
                var lot_name = event.target.attributes['data-lot'].value
                var lot_id = this.props.product_lots.filter(item => item.name == lot_name)[0]
                var arr = this.state.array.filter(item => item.text === lot_name)[0]
                
                if(entered_qty < 0){
                    $('i.decrease_lot_qty').css('opacity', '0.5');
                    $('i.increase_lot_qty').css('opacity', '1');
                    $('#qty_limit_warning').css('display', 'none');
                    event.target.value = 1;
                    arr.qty = 1;
                }else if(lot_id && entered_qty > lot_id.quantity){
                    $('i.decrease_lot_qty').css('opacity', '1');
                    $('#qty_limit_warning').css('display', 'block');
                    $('i.increase_lot_qty').css('opacity', '0.5');
                    event.target.value = lot_id.quantity;
                    arr.qty = lot_id.quantity;
                }else{
                    $('#qty_limit_warning').css('display', 'none');
                    $('i.decrease_lot_qty').css('opacity', '1');
                    $('i.increase_lot_qty').css('opacity', '1');
                    arr.qty = entered_qty;
                }

            }
            FormatValue(number) {
                var num = parseFloat(number);
                return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            }
            CheckExisting(lot){
                var self = this;
                if(self.state.array.filter(item => item.text === lot).length > 0){
                    return true;
                }
                return false;
            }
        };
    EditListPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        array: [],
        isSingleItem: false,
        product: false,
    
    };
    Registries.Component.extend(EditListPopup, ProductLotPopup);

    return EditListPopup;


});