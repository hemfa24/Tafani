odoo.define('dynamic_odoo.odoo_basic_fields', function (require) {
    "use strict";

    const {patch} = require('web.utils');
    var AbstractField = require('web.AbstractField');
    var {StatusBarField} = require("@web/views/fields/statusbar/statusbar_field");


    patch(StatusBarField.prototype, 'studio.StatusBarField', {
        get options() {
            const studioSelection = this.props.record.activeFields[this.props.name].rawAttrs.selection;
            if (studioSelection && this.props.record.fields[this.props.name].type == "selection") {
                return JSON.parse(studioSelection)
            }
            return this._super();
        },
        set options (options) {
        }
    });

    AbstractField.include({
        init: function (parent, name, record, options) {
            this._super(parent, name, record, options);
            if (this.field && this.field.type == "selection" && this.attrs.selection) {
                this.field.selection = JSON.parse(this.attrs.selection);
            }
        },
    });

});
