/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onWillUpdateProps, onPatched, onMounted } from "@odoo/owl";
import { formatFloat } from "@web/views/fields/formatters";


export class LocationsContainer extends Component {
    /*
    * The method to set up initial values
    */
    setup() {
        this.orm = useService("orm");
        this.state = useState({locationsElements: null});
        onWillStart(async () => {
            await this.onRenderLocations(this.props);
            this.maxLevel = await this.orm.call("stock.location", "action_get_max_expanded_level", []);
            this.decimalPrecision = await this.orm.call("stock.location", "action_get_decimal_precision", []);
        });
        onWillUpdateProps(async (nextProps) => {
            await this.onRenderLocations(nextProps);
        });
        onMounted(async() => {
            this.psbTable = $("#psb_table");
            this._hideToManyLevels();
        });
        onPatched(async() => {
            this._hideToManyLevels();
        });
    }
    qtyFormatFloat(value) {
        if (!value) { return 0 };
        return formatFloat(value, { humanReadable: true, decimals: this.decimalPrecision })
    }
    /*
    * The method to get locations and rerender the component
    */
    async onRenderLocations(nextProps) {
        var locationsElements = await this.orm.call(
            "stock.location", "action_prepare_elements_for_hierarchy", [nextProps.locations],
        );
        if (locationsElements.length == 0) {
            locationsElements = null;
        }
        Object.assign(this.state, { locationsElements: locationsElements});
    }
    /*
    * The method to hide/show levels based on level user clicks
    *  - In case we hide, we should hide also ALL children
    *  - In case we expand we should expand ONLY THE FIRST level
    */
    _onclickHide(event) {
        const currentLocationID = $(event.target).parent().parent().data("id");
        if ($(event.target).hasClass("fa-chevron-up")) { 
            this._hideRecursive(currentLocationID);
        }
        else {
            $(event.target).removeClass("fa-chevron-down").addClass("fa-chevron-up");
            this._expandFirstLevel(currentLocationID);
        };
    }
    /* 
     * The method to hide elements recursively
    */
    _hideRecursive(currentLocationID) {
        var self = this;
        const allRows = this.psbTable.find(".tr_location_class[location='" + currentLocationID + "']");
        const currentIcon = this.psbTable.find(".fa-chevron-up#" + currentLocationID);
        const iconRows = this.psbTable.find(".fa-chevron-up.o_hide[location='" + currentLocationID + "']");       
        currentIcon.removeClass("fa-chevron-up").addClass("fa-chevron-down");
        allRows.addClass("psb_hidden");        
        iconRows.removeClass("fa-chevron-up").addClass("fa-chevron-down");
        _.each(allRows, function (psbRow) {
            self._hideRecursive(psbRow.getAttribute("data-id"));
        });        
    }
    /*
     * The method to exapnd the very first hierarchy level
    */
    _expandFirstLevel(currentLocationID) {
        const currentIcon = this.psbTable.find(".fa-chevron-down#" + currentLocationID);
        const allRows = this.psbTable.find(".tr_location_class[location='" + currentLocationID + "']");
        currentIcon.removeClass("fa-chevron-down").addClass("fa-chevron-up");       
        allRows.removeClass("psb_hidden");
    }
    /*
     * The method to hide levels through the initial rendering based on max level
    */
    _hideToManyLevels() {
        var self = this;
        _.each(this.psbTable.find(".tr_location_class[level='" + this.maxLevel + "']"), function (psbRow) {
            self._hideRecursive(psbRow.getAttribute("data-id"));
        });
    }
    /*
     * The method to expand all levels
    */
    _onclickExpandAll(event) {
        var self = this;
        _.each(this.psbTable.find(".tr_location_class"), function (psbRow) {
            self._expandFirstLevel(psbRow.getAttribute("data-id"));
        });
    }
}

LocationsContainer.template = "product.stock.balance.locationsHierarchyWidgetContainer";
LocationsContainer.props = { locations: { type: Array } };
