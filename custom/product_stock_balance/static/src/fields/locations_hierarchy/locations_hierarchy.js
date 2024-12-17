/** @odoo-module */


import { Component } from "@odoo/owl";
import { LocationsContainer } from "@product_stock_balance/components/location_hierarchy_container/location_hierarchy_container";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks"


export class Many2ManyLocations extends Component {
    /*
    * The method to parse each line values
    */
    getLocationProps(record) {
        return {
            id: record.data.id,
            name: record.data.name,
            qty_available: record.data.qty_available,
            free_qty: record.data.free_qty,
            reserved_qty: record.data.reserved_qty,
            virtual_available: record.data.virtual_available,
            incoming_qty: record.data.incoming_qty,
            outgoing_qty: record.data.outgoing_qty,
        };
    }
    /*
    * The method to prepare the records for rpc action_prepare_elements_for_hierarchy of stock.location
    */
    get locations() {
        return this.props.value.records.map((record) => this.getLocationProps(record));
    }
}

Many2ManyLocations.template = "product.stock.balance.locationsHierarchyWidget";
Many2ManyLocations.components = { LocationsContainer };
Many2ManyLocations.props = { ...standardFieldProps };
Many2ManyLocations.supportedTypes = ["many2many"];
Many2ManyLocations.fieldsToFetch = {
    name: { type: "char" },
    qty_available: { type: "float" },
    free_qty: { type: "float" },
    reserved_qty: { type: "float" },
    virtual_available: { type: "float" },
    incoming_qty: { type: "float" },
    outgoing_qty: { type: "float" },
};

Many2ManyLocations.isSet = (value) => value.count > 0;

registry.category("fields").add("locationsHierarchyWidget", Many2ManyLocations);
