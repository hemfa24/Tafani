odoo.define('whatsapp_all_in_one.QRCodePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { useState } = owl;

    class QRCodePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ message: '', confirmButtonIsShown: false });
        }
    }
    QRCodePopup.template = 'QRCodePopup';
    QRCodePopup.defaultProps = {
        confirmText: _lt('Ok'),
        title: _lt('Scan QR Code'),
        body: '',
        cancelKey: true,
    };
    Registries.Component.add(QRCodePopup);
    return QRCodePopup;
});
