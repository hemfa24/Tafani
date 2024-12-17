/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState } = owl;

import {onMounted,  useEffect,onRendered, xml } from "@odoo/owl";
import rpc from 'web.rpc';
var time = require('web.time');
import session from 'web.session';



export class Timer_js extends Component {
    setup(params) {
        
        this.ormService = useService("orm");
        
        var res=super.setup(params);
        onMounted(async() => {
        var self = this;
        var def = await rpc.query({
            model: 'project.task',
            method: 'search_read',
            domain: [
                ['id', '=', this.props.record.resId],
            ],
        }).then(function (result) {
                var currentDate = new Date();
                self.duration = 0;
                _.each(result, function (data) {
                    self.duration += data.end_time ?
                        self._getDateDifference(data.start_time, data.end_time) :
                        self._getDateDifference(time.auto_str_to_date(data.start_time), currentDate);
                    
                });
            
        });
        this._startTimeCounter();
            // this.dialogs.add(MediaDialog, this.props);
        });
        return res   
    }

    // 

    destroy() {
        this._super.apply(this, arguments);
        clearTimeout(this.timer);
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Compute the difference between two dates.
     *
     * @private
     * @param {string} dateStart
     * @param {string} dateEnd
     * @returns {integer} the difference in millisecond
     */
    _getDateDifference(dateStart, dateEnd) {
        return moment(dateEnd).diff(moment(dateStart));
    }
    /**
     * @override
     */
    _render() {
        this._startTimeCounter();
    }
    /**
     * @private
     */
    _startTimeCounter() {
        var self = this;
        clearTimeout(this.timer);
        if (this.props.record.data.task_Start) {
            this.timer = setTimeout(function () {
                self.duration += 1000;
                self._startTimeCounter();
            }, 1000);
        } else {
            clearTimeout(this.timer);
        }
        const duration = moment.duration(this.duration, 'milliseconds');
        const hours = Math.floor(duration.asHours());
        const minutes = duration.minutes();
        const seconds = duration.seconds();
        //display the variables in two-character format, e.g: 09 intead of 9
        const text = _.str.sprintf("%02d:%02d:%02d", hours, minutes, seconds);
        const $mrpTimeText = $('<span>', { text });
        $(this.__owl__.bdom.el).empty().append($mrpTimeText);
        
    }
    
}
Timer_js.template = "bi_all_in_one_project_management_system.timer";

registry.category("fields").add("timer_concept", Timer_js);
