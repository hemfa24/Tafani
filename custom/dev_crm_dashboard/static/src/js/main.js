odoo.define('dev_crm_dashboard.main', function (require) { 
"use strict";

    var AbstractAction = require('web.AbstractAction'); 
	var session = require('web.session');
	var rpc = require('web.rpc');
	var utils = require('web.utils');
	var Dialog = require('web.Dialog');
	var time = require('web.time');
	var datepicker = require('web.datepicker');
	var round_di = utils.round_decimals;
	var core = require('web.core');
	var QWeb = core.qweb;
	var _t = core._t;

    
	var crmDashboard = AbstractAction.extend( {
	    title: core._t('CRM Dashboard'),
	    template: 'crmDashboardAction',
	    events: {
	        'click .action_all_leads': 'action_all_leads',
	        'click .navigate_new_customer': 'navigate_new_customer',
	        'click .navigate_all_activities': 'navigate_all_activities',
	        'change .users-option': 'action_change_user_filter',
	        'change .partners-option': 'action_change_partner_filter',
	        'click .dev-action-view-lead': '_on_click_menu_view_lead', 
	        'change .date-based-filter' : '_on_change_date_based_filter',
	        'change .top-won-customer-chart' : '_on_change_top_won_customer_chart',
	        'change .top-won-customer-filter' : '_on_change_top_won_customer_chart',
	        'change .top-sale-team-opportunity-chart' : '_on_change_top_won_customer_chart',
	        'change .top-sale-team-opportunity-number-filter' : '_on_change_top_won_customer_chart',
	        'change .top-expected-revenue-chart' : '_on_change_top_won_customer_chart',
	        'change .top-expected-revenue-number-filter' : '_on_change_top_won_customer_chart',
	        'change .top-lost-chart-filter' : '_on_change_top_won_customer_chart',
	        'change .top-lost-chart-number-filter' : '_on_change_top_won_customer_chart',
	        'change .priority-lead-chart-filter' : '_on_change_top_won_customer_chart',
	        'change .lead-priority-filter' : '_on_change_top_won_customer_chart',
	        'change .priority-pipeline-chart-filter' : '_on_change_top_won_customer_chart',
	        'change .pipeline-priority-filter' : '_on_change_top_won_customer_chart',
	        'click .dev-menu-action-all-activity': '_on_click_menu_action_all_activity',
	        'click .dev-menu-action-view-record': '_on_click_menu_action_view_record',
//	        'click .dev-export-record': '_on_click_export_excel',
	        
	    },
	    
	    
	    init: function (parent, params) {
	        this._super.apply(this, arguments);
	    },
	    start: function () {
	        this.set("title", this.title);
	        this.init_filters();
	        this.load_invoices();
	        this.init_chart();
	    },
	    getContext: function () {
            var context = {
                DateFilterStartDate: this.DateFilterStartDate,
                DateFilterEndDate: this.DateFilterEndDate,
            }
            return Object.assign(context)
        },
        
        _on_change_top_won_customer_chart: function(event){
        	var self = this;
        	var value = $(event.currentTarget).val();
        	if(value == 'custom_range'){
        		if (!self.StartDatePickerWidget){
    	    		this.StartDatePickerWidget = new (datepicker.DateWidget)(this);
    	        }
    	    	if (!self.EndDatePickerWidget){
    	    		this.EndDatePickerWidget = new (datepicker.DateWidget)(this);
    	        }
	    		if(self.StartDatePickerWidget){
	    			self.StartDatePickerWidget.appendTo($(".date_input_fields")).then((function () {
	            		self.StartDatePickerWidget.$el.addClass("btn_middle_child o_input");
	            		self.StartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
	            		self.StartDatePickerWidget.on("datetime_changed", self, function () {
	                        $(".apply-dashboard-date-filter").removeClass("d-none");
	                        $(".clear-dashboard-date-filter").removeClass("d-none");
	                    });
	                }).bind(self));
	    		}
            	if(self.EndDatePickerWidget){
            		self.EndDatePickerWidget.appendTo($(".date_input_fields")).then((function () {
                		self.EndDatePickerWidget.$el.addClass("btn_middle_child o_input");
                		self.EndDatePickerWidget.$el.find("input").attr("placeholder", "End Date");
                		self.EndDatePickerWidget.on("datetime_changed", self, function () {
                            $(".apply-dashboard-date-filter").removeClass("d-none");
                            $(".clear-dashboard-date-filter").removeClass("d-none");
                        });
                    }).bind(self));
            	}
            	self.show_date_range_block();
        	} else {
        	
        		self.hide_date_range_block();
        		self.load_data_top_won_customer_chart();
        		self.init_chart();
        	}
        },
        
        
        load_data_top_won_customer_chart: function(){
	    	var self = this;
	    	var args = [];
	    	var vals = {};
	    	 var user_id = $('.users-option').val();
	    	 var partner_id = $('.partners-option').val();
             if(Number(user_id) > 0){
            	 vals['user_id'] = user_id;
	    	}
            if(Number(partner_id) > 0){
            	 vals['partner_id'] = partner_id;
	    	}
            self.company_id = session.company_id;
            if(self.company_id){
            	vals['company_id'] = self.company_id;
            }
            var date_opt = $('.date-based-filter').val();
            if(date_opt && date_opt != 'custom_range'){
            	vals['date_opt'] = date_opt;
            }
            var chart_opt = $('.top-won-customer-chart').val(); 
            if(chart_opt && chart_opt != 'custom_range'){
            	vals['top_won_customer_chart_type'] = chart_opt;
            }
            var chart_opt = $('.top-won-customer-filter').val(); 
            if(chart_opt && chart_opt != 'custom_range'){
            	vals['top_won_customer_filter'] = chart_opt;
            }
            
            var sale_team_opportunity_chart = $('.top-sale-team-opportunity-chart').val(); 
            if(sale_team_opportunity_chart && sale_team_opportunity_chart != 'custom_range'){
            	vals['top_sale_team_opportunity_chart'] = sale_team_opportunity_chart;
            }
            var sale_team_opportunity_number = $('.top-sale-team-opportunity-number-filter').val(); 
            if(sale_team_opportunity_number && sale_team_opportunity_number != 'custom_range'){
            	vals['sale_team_opportunity_number'] = sale_team_opportunity_number;
            }
            
            var top_expected_revenue_chart = $('.top-expected-revenue-chart').val(); 
            if(top_expected_revenue_chart && top_expected_revenue_chart != 'custom_range'){
            	vals['top_expected_revenue_chart'] = top_expected_revenue_chart;
            }
            var top_expected_revenue_number = $('.top-expected-revenue-number-filter').val(); 
            if(top_expected_revenue_number && top_expected_revenue_number != 'custom_range'){
            	vals['top_expected_revenue_number'] = top_expected_revenue_number;
            }
            
            
            var top_lost_chart_filter = $('.top-lost-chart-filter').val(); 
            if(top_lost_chart_filter && top_lost_chart_filter != 'custom_range'){
            	vals['top_lost_chart_filter'] = top_lost_chart_filter;
            }
            var top_lost_chart_number_filter = $('.top-lost-chart-number-filter').val(); 
            if(top_lost_chart_number_filter && top_lost_chart_number_filter != 'custom_range'){
            	vals['top_lost_chart_number_filter'] = top_lost_chart_number_filter;
            }
            
            var priority_lead_chart_filter = $('.priority-lead-chart-filter').val(); 
            if(priority_lead_chart_filter && priority_lead_chart_filter != 'custom_range'){
            	vals['priority_lead_chart_filter'] = priority_lead_chart_filter;
            }
            var lead_priority_filter = $('.lead-priority-filter').val(); 
            if(lead_priority_filter && lead_priority_filter != 'custom_range'){
            	vals['lead_priority_filter'] = lead_priority_filter;
            }
            
            var priority_pipeline_chart_filter = $('.priority-pipeline-chart-filter').val(); 
            if(priority_pipeline_chart_filter && priority_pipeline_chart_filter != 'custom_range'){
            	vals['priority_pipeline_chart_filter'] = priority_pipeline_chart_filter;
            }
            var pipeline_priority_filter = $('.pipeline-priority-filter').val(); 
            if(pipeline_priority_filter && pipeline_priority_filter != 'custom_range'){
            	vals['pipeline_priority_filter'] = pipeline_priority_filter;
            }
            
            
	    	var params = {
        		model: 'crm.lead',
        		method: 'load_server_data_for_dashboard',
        		args: [vals],
        		context: self.getContext(),
        	}
        	rpc.query(params, {async: false})
            .then(function(result){
            	self.server_response = result;
            	if(result){
            		if(result.journals && result.journals.length){
            			self.journals = result.journals
            		}
            		var boxes = QWeb.render('HelpdeskRows', {
    	            	'response':result,
    	            	'widget':self,
    	            });
            	}
            });
	    },
        
        
        
        _on_change_date_based_filter: function(event){
        	var self = this;
        	var value = $(event.currentTarget).val();
        	if(value == 'custom_range'){
        		if (!self.StartDatePickerWidget){
    	    		this.StartDatePickerWidget = new (datepicker.DateWidget)(this);
    	        }
    	    	if (!self.EndDatePickerWidget){
    	    		this.EndDatePickerWidget = new (datepicker.DateWidget)(this);
    	        }
	    		if(self.StartDatePickerWidget){
	    			self.StartDatePickerWidget.appendTo($(".date_input_fields")).then((function () {
	            		self.StartDatePickerWidget.$el.addClass("btn_middle_child o_input");
	            		self.StartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
	            		self.StartDatePickerWidget.on("datetime_changed", self, function () {
	                        $(".apply-dashboard-date-filter").removeClass("d-none");
	                        $(".clear-dashboard-date-filter").removeClass("d-none");
	                    });
	                }).bind(self));
	    		}
            	if(self.EndDatePickerWidget){
            		self.EndDatePickerWidget.appendTo($(".date_input_fields")).then((function () {
                		self.EndDatePickerWidget.$el.addClass("btn_middle_child o_input");
                		self.EndDatePickerWidget.$el.find("input").attr("placeholder", "End Date");
                		self.EndDatePickerWidget.on("datetime_changed", self, function () {
                            $(".apply-dashboard-date-filter").removeClass("d-none");
                            $(".clear-dashboard-date-filter").removeClass("d-none");
                        });
                    }).bind(self));
            	}
            	self.show_date_range_block();
        	} else {
        		self.hide_date_range_block();
        		self.load_invoices();
        		self.init_chart();
        	}
        },
        show_date_range_block: function(){
        	$('.date_input_fields').show();
        	$('.apply-dashboard-date-filter').removeClass('d-none');
        	$('.clear-dashboard-date-filter').removeClass('d-none');
        },
        hide_date_range_block: function(){
        	$('.date_input_fields').attr("style", "display: none !important");
    		$('.apply-dashboard-date-filter').addClass('d-none');
    		$('.clear-dashboard-date-filter').addClass('d-none');
        },
        _onClearDateValues: function () {
            this.DateFilterStartDate = false;
            this.DateFilterEndDate = false;
            this.load_invoices();
            this.StartDatePickerWidget.setValue(false);
            this.EndDatePickerWidget.setValue(false);
        },
        
        
//        _on_click_export_excel: function(ev){
//            var self = this;
//            var chart_type = document.getElementsByClassName("top-won-customer-chart");
//            var top_won_customer = document.getElementsByClassName("top-won-customer-filter");
//            var users_option = document.getElementsByClassName("users-option");
////            var rec_id = $(ev.currentTarget).attr('rec-id')
//            console.log("dadad========?",chart_type[0].value);
//            console.log("top_won_customer========?",top_won_customer[0].value);
//            console.log("users_option========?",users_option[0].value);
//            var params = {
//	            		model: 'crm.lead',
//	            		method: 'action_print_excel_report',
//	            		args: [Number(0)],
//	            		context : {'chart_type':chart_type[0].value,'top_won_customre':top_won_customer[0].value}
//	            	}
//        	rpc.query(params)
//        },
        
        
        _on_click_menu_action_all_activity: function(ev){
        	var self = this;
	    	var rec_id = $(ev.currentTarget).attr('rec-id')
	    	var action_type = $(ev.currentTarget)[0].id;
	    	if(action_type == 'view'){
	    		self.do_action({
	                type: 'ir.actions.act_window',
	                res_model: 'mail.activity',
	                res_id: Number(rec_id),
	                views: [[false, 'form']],
	                target: 'current'
	            });
	    	} 
        },
        _on_click_menu_action_view_record: function(ev){
        	var self = this;
	    	var model = $(ev.currentTarget).attr('model')
	    	var rec_id = $(ev.currentTarget).attr('res_id')
	    	var action_type = $(ev.currentTarget)[0].id;
//	    	if(action_type == 'view'){
    		self.do_action({
                type: 'ir.actions.act_window',
                res_model: model,
                res_id: Number(rec_id),
                views: [[false, 'form']],
                target: 'current'
            });
//	    	} 
        },
        
        _on_click_menu_view_lead: function(ev){
        	var self = this;
	    	var rec_id = $(ev.currentTarget).attr('rec-id')
	    	var action_type = $(ev.currentTarget)[0].id;
	    	if(action_type == 'view'){
	    		self.do_action({
	                type: 'ir.actions.act_window',
	                res_model: 'crm.lead',
	                res_id: Number(rec_id),
	                views: [[false, 'form']],
	                target: 'current'
	            });
	    	} 
        },
	    _onApplyDateFilter: function (e) {
            var self = this;
            var start_date = self.StartDatePickerWidget.getValue();
            var end_date = self.EndDatePickerWidget.getValue();
            if (start_date === "Invalid date") {
                alert("Invalid Start Date!.")
            } else if (end_date === "Invalid date") {
                alert("Invalid End Date!.")
            } else {
                if (start_date && end_date) {
                    if (start_date <= end_date) {
                        self.DateFilterStartDate = start_date.add(-this.getSession().getTZOffset(start_date), 'minutes');
                        self.DateFilterEndDate = end_date.add(-this.getSession().getTZOffset(start_date), 'minutes');
                    	self.load_invoices();
                    	self.init_chart();
                    } else {
                        alert(_t("Start date should be less than end date"));
                    }
                } else {
                    alert(_t("Please enter start date and end date"));
                }
            }
        },
        
//        bellow method used for default load Chart and filter
        
        init_chart: function(){
	    	var self = this;
	    	var params = {
        		model: 'crm.lead',
        		method: 'load_users_and_partners',
        		args: [],
        	}
        	rpc.query(params, {async: false})
            .then(function(result){
                var title = "Top "+ String(self.server_response.top_won_customer_number_filter) +" Won Customer " + self.server_response.won_pipeline_chart_type + " Chart"
            	var chart = new CanvasJS.Chart("chartContainer_1", {
	            	theme: "light2",
	            	
                    title:{
                        
	                    text: title             
                    },
                    data: self.server_response.won_pipeline_chart_data
	            });
            	chart.render();
        	    var title_2 = "Top "+ String(self.server_response.top_sale_team_pipeline_filter_number) +" Sale Team pipeline " + self.server_response.top_sale_team_pipeline_chart_type + " Chart"
            	var chart_2 = new CanvasJS.Chart("chartContainer_2", {
	            	theme: "light2",
                    title:{
	                    text: title_2              
                    },
                    data: self.server_response.top_sale_team_pipeline_chart_data
	            });
            	chart_2.render();
            	var title_3 = "Top "+ String(self.server_response.top_expected_revenue_number) +" Expected Revenue " + self.server_response.top_expected_revenue_chart_type + " Chart"
            	var chart_3 = new CanvasJS.Chart("chartContainer_3", {
	            	theme: "light2",
                    title:{
	                    text: title_3              
                    },
                    data : self.server_response.top_expected_revenue_chart_data
	            });
            	chart_3.render();
            	var title_4 = "Top "+ String(self.server_response.top_lost_chart_number_filter) +" Lost Customer " + self.server_response.top_lost_chart_type + " Chart"
            	var chart_4 = new CanvasJS.Chart("chartContainer_4", {
	            	theme: "light2",
                    title:{
	                    text: title_4              
                    },
                    data : self.server_response.top_lost_chart_data
	            });
            	chart_4.render();
            	var title_5 = "Lead "+ String(self.server_response.lead_priority_name)+" " + self.server_response.priority_wise_lead_chart_type + " Chart"
            	var chart_5 = new CanvasJS.Chart("chartContainer_5", {
	            	theme: "light2",
                    title:{
	                    text: title_5              
                    },
                    data : self.server_response.priority_wise_lead_chart
	            });
            	chart_5.render();
            	var title_6 = "Pipeline "+ String(self.server_response.pipeline_priority_name)+" " + self.server_response.priority_wise_pipline_chart_type + " Chart"
            	var chart_6 = new CanvasJS.Chart("chartContainer_6", {
	            	theme: "light2",
                    title:{
	                    text: title_6              
                    },
                    data : self.server_response.priority_wise_pipeline_chart_data
	            });
            	chart_6.render();
            });
	    },
        
        
	    init_filters: function(){
	    	var self = this;
	    	var params = {
        		model: 'crm.lead',
        		method: 'load_users_and_partners',
        		args: [],
        	}
        	rpc.query(params, {async: false})
            .then(function(result){
            	var filters = QWeb.render('ActivityFilter', {
	            	'users':result.users,
	            	'partners':result.partners,
//	            	'charts':result.charts,
	            	'widget':self,
	            });
            	self.users = result
            	$('.filter-header').html(filters);
            });
	    },
	    get_report_url: function(id){
	    	var url = "/dashboard/invoices/"+Number(id)+"?report_type=pdf&amp;download=true";
	    	return url;
	    },
	    load_invoices: function(){
	    	var self = this;
	    	var args = [];
	    	var vals = {};
	    	 var user_id = $('.users-option').val();
	    	 var partner_id = $('.partners-option').val();
             if(Number(user_id) > 0){
            	 vals['user_id'] = user_id;
	    	}
            if(Number(partner_id) > 0){
            	 vals['partner_id'] = partner_id;
	    	}
            self.company_id = session.company_id;
            if(self.company_id){
            	vals['company_id'] = self.company_id;
            }
            var date_opt = $('.date-based-filter').val();
            if(date_opt && date_opt != 'custom_range'){
            	vals['date_opt'] = date_opt;
            }
//            
            
            
            
            
            
	    	var params = {
        		model: 'crm.lead',
        		method: 'load_server_data_for_dashboard',
        		args: [vals],
        		context: self.getContext(),
        	}
        	rpc.query(params, {async: false})
            .then(function(result){
            	self.server_response = result;
            	if(result){
            		if(result.journals && result.journals.length){
            			self.journals = result.journals
            		}
            		var boxes = QWeb.render('HelpdeskCountBoxes', {
    	            	'response':result,
    	            	'widget':self,
    	            });
                	$('.activity_count_boxes').html(boxes);
                	var invoice_list_view = QWeb.render('HelpdeskRows', { 
                		'widget':self,
                		'all_leads_list': result.all_leads_list || [],
                		'table_title_draft_appointment': '# Leads',
                		'my_pipeline_list':result.my_pipeline_list || [],
                		'my_pipeline_list_title': '# Pipeline',
                		'list_all_activity':result.list_all_activity || [] ,
                		'list_all_activity_title': '# Activities',
                		'upcoming_activity': result.upcoming_activity || [],
                	});
                	$('.helpdesk-table-container').html(invoice_list_view);
            	}
            });
	    },
	    action_all_leads: function(ev){
	    	var self = this;
	    	var action = $(ev.currentTarget)[0] ? $(ev.currentTarget)[0].id : false;
	    	var domain = false;
	    	if(!action){
	    		return
	    	}
	    	if(action == 'navigate_all_leads'){
	    		domain = [['id','in',_.pluck(self.server_response.all_leads, 'id')]];
	    	} else if (action == 'navigate_my_pipeline'){
	    		domain = [['id','in',_.pluck(self.server_response.my_pipeline, 'id')]];
	    	} else if (action == 'navigate_won'){
	    		domain = [['id','in',_.pluck(self.server_response.all_won_pipeline, 'id')]];
	    	} 
	    	self.do_action({
                name: _t('Appointment '),
                type: 'ir.actions.act_window',
                view_mode: 'tree',
                res_model: 'crm.lead',
                domain: domain ,
                context: {
                    search_default_no_share: true,
                },
                views: [[false, 'list'],[false, 'form']],
            });
	    },
	    
	    
	    
	    navigate_new_customer: function(ev){
	    	var self = this;
	    	var action = $(ev.currentTarget)[0] ? $(ev.currentTarget)[0].id : false;
	    	var domain = false;
	    	if(!action){
	    		return
	    	}
	    	if(action == 'navigate_new_customer'){
	    		domain = [['id','in',_.pluck(self.server_response.new_customer_record, 'id')]];
	    	} 
	    	self.do_action({
                name: _t('Customers'),
                type: 'ir.actions.act_window',
                view_mode: 'tree',
                res_model: 'res.partner',
                domain: domain ,
                context: {
                    search_default_no_share: true,
                },
                views: [[false, 'list'],[false, 'form']],
            });
	    },
	    
	    navigate_all_activities: function(ev){
	    	var self = this;
	    	var action = $(ev.currentTarget)[0] ? $(ev.currentTarget)[0].id : false;
	    	var domain = false;
	    	if(!action){
	    		return
	    	}
	    	if(action == 'navigate_all_activities'){
	    		domain = [['id','in',_.pluck(self.server_response.all_activity, 'id')]];
	    	} 
	    	self.do_action({
                name: _t('All Activities'),
                type: 'ir.actions.act_window',
                view_mode: 'tree',
                res_model: 'mail.activity',
                domain: domain ,
                context: {
                    search_default_no_share: true,
                },
                views: [[false, 'list'],[false, 'form']],
            });
	    },
	    
	    
	    action_change_user_filter: function(ev){
	    	this.load_invoices();
	    	this.init_chart();
	    	this.load_data_top_won_customer_chart()
	    },
	    action_change_partner_filter: function(ev){
	    	this.load_invoices();
	    	this.init_chart();
	    	this.load_data_top_won_customer_chart();
	    },
	});

	core.action_registry.add('open_crm_dashboard', crmDashboard);
//	return InvoiceDashboard

	return {
		crmDashboard: crmDashboard, 
	};

});
