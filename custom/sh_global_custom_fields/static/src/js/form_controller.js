/** @odoo-module **/

import { patch } from 'web.utils';

import { FormController } from "@web/views/form/form_controller";

const components = { FormController };
import { useService } from "@web/core/utils/hooks";
var rpc = require("web.rpc");

var can_create_custom_field = false;
var session = require('web.session');
session.user_has_group("sh_global_custom_fields.group_global_custom_field").then(function (has_group) {
  can_create_custom_field = has_group;
});

patch(components.FormController.prototype, 'sh_global_custom_fields/static/src/js/form_controller.js', {

    setup(...args) {

        this._super(...args)
        this.actionService = useService('action');
    },
	getActionMenuItems() {
        const otherActionItems = [];
        if (this.archiveEnabled) {
            if (this.model.root.isActive) {
                otherActionItems.push({
                    key: "archive",
                    description: this.env._t("Archive"),
                    callback: () => {
                        const dialogProps = {
                            body: this.env._t(
                                "Are you sure that you want to archive all this record?"
                            ),
                            confirm: () => this.model.root.archive(),
                            cancel: () => {},
                        };
                        this.dialogService.add(ConfirmationDialog, dialogProps);
                    },
                });
            } else {
                otherActionItems.push({
                    key: "unarchive",
                    description: this.env._t("Unarchive"),
                    callback: () => this.model.root.unarchive(),
                });
            }
        }
        if (this.archInfo.activeActions.create && this.archInfo.activeActions.duplicate) {
            otherActionItems.push({
                key: "duplicate",
                description: this.env._t("Duplicate"),
                callback: () => this.duplicateRecord(),
            });
        }
        if (this.archInfo.activeActions.delete) {
            otherActionItems.push({
                key: "delete",
                description: this.env._t("Delete"),
                callback: () => this.deleteRecord(),
            });
        }
        if (can_create_custom_field) {
          otherActionItems.push({
        	  key: "create_custom_field",
              description: this.env._t("Create Custom Field"),
              callback: () => this.onCreateCustomField(),
          });
          otherActionItems.push({
        	  key: "create_custom_tab",
              description: this.env._t("Create Custom Tab"),
              callback: () => this.onCreateCustomTab(),
          });
      }
        return Object.assign({}, this.props.info.actionMenus, { other: otherActionItems });
    },
	
   onCreateCustomField: function () {
    	
        var self = this;
        var model_name =this.actionService.currentController.action.res_model
        var view_id = false
            rpc.query({
                model: 'ir.ui.view',
                method: 'search_read',
                fields: ['id'],
                domain: [['model', '=', model_name],['type','=','form'],['mode','=','primary']],
                order: 'sequence desc',
                limit: 1,
            }, { async: false }).then(function (data) {
                if(data && data[0]){
                    view_id = data[0]['id']
                    self._CreateCustomField(view_id);
                }
            });

		
   },
   onCreateCustomTab: function () {
        var self = this;
        var model_name =this.actionService.currentController.action.res_model
        var view_id = false
            rpc.query({
                model: 'ir.ui.view',
                method: 'search_read',
                fields: ['id'],
                domain: [['model', '=', model_name],['type','=','form'],['mode','=','primary']],
                order: 'sequence desc',
                limit: 1,
            }, { async: false }).then(function (data) {
                if(data && data[0]){
                    view_id = data[0]['id']
                    self._CreateCustomTab(view_id);
                }
            });

      
   },
   _CreateCustomField: function (view_id) {
		 var self = this;
	    
	       var model_name =this.actionService.currentController.action.res_model
	       var actionViews = this.actionService.currentController.action.views
	       _.each(actionViews, function (view) {
	    	   if (view.length > 0 && view[1] == "form") {
	                   self.actionService.doAction({
	                       res_model: "sh.custom.field.model",
	                       name: self.env._t("Create Custom Field"),
	                       views: [[false, "form"]],
	                       target: "new",
	                       type: "ir.actions.act_window",
	                       context: {
	                           default_parent_view_id: view_id,
	                           default_parent_model: model_name,
	                       },
	                   });
	           }
	       });
   },
   _CreateCustomTab: function (view_id) {
       var self = this;
       var model_name =this.actionService.currentController.action.res_model
       var actionViews = this.actionService.currentController.action.views
       _.each(actionViews, function (view) {
           if (view.length > 0 && view[1] == "form") {
			       self.actionService.doAction({
			           res_model: "sh.custom.model.tab",
                       name: self.env._t("Create Custom Tab"),
                       views: [[false, "form"]],
                       target: "new",
                       type: "ir.actions.act_window",
                       context: {
                           default_parent_view_id: view_id,
                           default_parent_model: model_name,
                       },
                   });
  
           }
       });
   },
		 
	
});
