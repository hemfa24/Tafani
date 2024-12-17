odoo.define('whatsapp_all_in_one.WhatsAppReceiptScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const { onMounted, useRef, status } = owl;
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const { Printer } = require('point_of_sale.Printer');
    const { Gui } = require('point_of_sale.Gui');


    const WhatsAppButton = (AbstractReceiptScreen) => {
        class WhatsAppButton extends AbstractReceiptScreen {
            setup() {
                super.setup();
                this.orderReceiptWhatsApp = useRef('order-receipt');
            }
            async sendToWhatsApp() {
                var order = this.env.pos.get_order();
                var self = this;
                var customer = order.partner;
                if (!customer) {
                    Gui.showPopup('ErrorPopup', {
                        title: this.env._t('No customer'),
                        body: this.env._t('Customer is not selected! Please selected customer to send order receipt.'),
                    });
                    return;
                }
                if (customer && !customer.mobile) {
                    Gui.showPopup('ErrorPopup', {
                        title: this.env._t('No mobile number'),
                        body: this.env._t('Can not send WhatsApp message. Mobile number is not available for this customer.'),
                    });
                    return;
                }
                if (!order) {
                    Gui.showPopup('ErrorPopup', {
                        title: this.env._t('No Orer'),
                        body: this.env._t('No order available in the system.'),
                    });
                }

                var receiptData = {};
                if (this.orderReceipt && this.orderReceipt.el && this.orderReceipt.el.outerHTML) {
                    receiptData = this.orderReceipt.el.outerHTML;
                } else {
                    receiptData = this.__owl__.parent.refs['order-receipt'];
                    if (receiptData && receiptData.childNodes) {
                        receiptData = receiptData.childNodes[0] && receiptData.childNodes[0].outerHTML;
                    }
                }
                // const printer = new Printer(null, this.env.pos);
                // const ticketImage = await printer.htmlToImg(receiptData);
                var is_send_invoice = order.is_to_invoice();
                var message = '';
                if (is_send_invoice) {
                    message = self.env._t('Dear *' + customer.name + '*,\nHere is your Invoice for the *' + order.name + '*');
                } else {
                    message = self.env._t('Dear *' + customer.name + '*,\nHere is your electronic ticket for the *' + order.name + '*');
                }
                var newContext = {
                    'receipt_data': receiptData,
                    'active_model': 'pos.order',
                    'active_id': order.name,
                };
                var context = _.extend(this.env.session.user_context || {}, newContext);

                await this.rpc({
                    model: 'whatsapp.msg',
                    method: 'create',
                    args: [{
                        'partner_ids': [customer.id],
                        'message': message,
                    }],
                    kwargs: { context: newContext },
                }).then(function(result) {
                    if (result) {
                        self.rpc({
                            model: 'whatsapp.msg',
                            method: 'action_send_msg',
                            args: [[result]],
                            kwargs: { context: {'from_pos': true} },
                        }).then(function (res) {
                            var type = is_send_invoice ? "Invoice" : "Receipt";
                            if (res && res.name && res.name === 'Scan WhatsApp QR Code') {
                                Gui.showPopup('QRCodePopup', { qr_img: res.qr_img , rec_id: result, type: type });
                                return false;
                            } else if (res === true) {
                                const {confirmed} = Gui.showPopup('ConfirmPopup', {
                                    title: self.env._t('Message Sent'),
                                    body: self.env._t('Message sent to customer.'),
                                });
                                if (confirmed) {
                                    return true;
                                }
                            } else {
                                Gui.showPopup('ErrorPopup', {
                                    title: self.env._t('Error sending message'),
                                    body: self.env._t('Something went wrong while sending ' + type + ' to WhatsApp.'),
                                });
                            }
                        });
                    }
                });
            }
        }
        WhatsAppButton.template = 'WhatsAppButton';
        return WhatsAppButton;
    };
    Registries.Component.addByExtending(WhatsAppButton, AbstractReceiptScreen);
    return WhatsAppButton;

});
