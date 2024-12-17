# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from operator import itemgetter
import itertools
from operator import itemgetter
import operator

class crm_lead(models.Model):
    _inherit = 'crm.lead'
    
    
    


    @api.model
    def load_server_data_for_dashboard(self,vals={}):
        lead_domain,my_pipeline_domain ,new_customer_domain,all_activity_domain = [], [],[],[]
        query_lead_domain = []
        date_val = vals.get('date_opt')
        def sd(date):
            return fields.Datetime.to_string(date)
        
        def previous_week_range(date):
            start_date = date + datetime.timedelta(-date.weekday(), weeks=-1)
            end_date = date + datetime.timedelta(-date.weekday() - 1)
            return {'start_date':start_date.strftime('%Y-%m-%d %H:%M:%S'), 'end_date':end_date.strftime('%Y-%m-%d %H:%M:%S')}

        lead_domain_query = []
        lead_domain_value = () 
        pipeline_domain_query = []
        new_customer_domain_query = []
        
        if vals.get('user_id'):
            lead_domain += [('user_id','=',int(vals.get('user_id')))]
            lead_domain_query.append("%s = %s" % ('c_lead.user_id',vals.get('user_id')))
            pipeline_domain_query.append("%s = %s" % ('c_lead.user_id',vals.get('user_id')))
            
        if vals.get('partner_id'):
            lead_domain += [('partner_id','=',int(vals.get('partner_id')))]
            lead_domain_query.append("%s = %s" % ('c_lead.partner_id',vals.get('partner_id')))
            pipeline_domain_query.append("%s = %s" % ('c_lead.partner_id',vals.get('partner_id')))
            
        
            
        start_date_ctx = self._context.get('DateFilterStartDate', False)
        end_date_ctx = self._context.get('DateFilterEndDate', False)

        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(datetime.datetime.today() + relativedelta(days=-today.weekday())) + datetime.timedelta(days=7))
        week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
        month_ago = (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        starting_of_year = datetime.datetime.now().date().replace(month=1, day=1)    
        ending_of_year = datetime.datetime.now().date().replace(month=12, day=31)
        if start_date_ctx and end_date_ctx:
            lead_domain += [('date_deadline','>=',start_date_ctx),('date_deadline','<=',end_date_ctx)]
            
            new_customer_domain += [('create_date','>=',start_date_ctx),('create_date','<=',end_date_ctx)]
            all_activity_domain += [('date_deadline','>=',start_date_ctx),('date_deadline','<=',end_date_ctx)]
            
        lead_domain_value = ()
        if date_val and date_val == 'today' or date_val == None:
            lead_domain += [('date_deadline', '>=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),
             ('date_deadline', '<=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]
             
             
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=(datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00'),
                datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59')
             )
             
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]
             
            
            
            
            new_customer_domain += [('create_date', '>=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),
             ('create_date', '<=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]
            all_activity_domain += [('date_deadline', '>=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),
             ('date_deadline', '<=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]
             
        if date_val and date_val == 'yesterday':
            lead_domain += [('date_deadline', '>=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00')),
                       ('date_deadline', '<=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))]
                    
           
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=(datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00'),
                datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))
                
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
            
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]
            new_customer_domain += [('create_date', '>=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00')),('create_date', '<=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))]
            all_activity_domain += [('date_deadline', '>=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00')),
                       ('date_deadline', '<=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))]
            
        if date_val and date_val == 'current_week':
            lead_domain += [('date_deadline', '>=', sd(datetime.datetime.today() + relativedelta(days=-today.weekday()))), 
                       ('date_deadline', '<=', this_week_end_date)]
                       
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=( sd(datetime.datetime.today() + relativedelta(days=-today.weekday())),
                                this_week_end_date
                                )
            
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
             
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]   
            
            new_customer_domain += [('create_date', '>=', sd(datetime.datetime.today() + relativedelta(days=-today.weekday()))), 
                       ('create_date', '<=', this_week_end_date)]
            all_activity_domain += [('date_deadline', '>=', sd(datetime.datetime.today() + relativedelta(days=-today.weekday()))), 
                       ('date_deadline', '<=', this_week_end_date)]
#           
        if date_val and date_val == 'last_7_days':
            lead_domain += [('date_deadline', '>=', sd(week_ago)), ('date_deadline', '<=', sd(datetime.datetime.today()))]
            
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=( sd(datetime.datetime.today() + relativedelta(days=-today.weekday())),
                                this_week_end_date
                                )
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
            
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]  
            new_customer_domain += [('create_date', '>=', sd(week_ago)), ('create_date', '<=', sd(datetime.datetime.today()))]
            all_activity_domain += [('date_deadline', '>=', sd(week_ago)), ('date_deadline', '<=', sd(datetime.datetime.today()))]
        if date_val and date_val == 'last_week':
            lead_domain += [('date_deadline', '>=', previous_week_range(datetime.datetime.today()).get('start_date')), 
            ('create_date', '<=', previous_week_range(datetime.datetime.today()).get('end_date'))]
            
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=( previous_week_range(datetime.datetime.today()).get('start_date'),
                                previous_week_range(datetime.datetime.today()).get('end_date') 
                            )
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.create_date <= %s")]
            
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]  
            
            new_customer_domain += [('create_date', '>=', previous_week_range(datetime.datetime.today()).get('start_date')), ('create_date', '<=', previous_week_range(datetime.datetime.today()).get('end_date'))]
            all_activity_domain += [('date_deadline', '>=', previous_week_range(datetime.datetime.today()).get('start_date')), ('create_date', '<=', previous_week_range(datetime.datetime.today()).get('end_date'))]
        if date_val and date_val == 'current_month':
            lead_domain += [
                       ("date_deadline", ">=", sd(today.replace(day=1))),
                       ("date_deadline", "<=", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 23:59:59'))
                    ]
            
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=( sd(today.replace(day=1)),
                                (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 23:59:59')
                                )
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
                    
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]  
            new_customer_domain += [
                       ("create_date", ">=", sd(today.replace(day=1))),
                       ("create_date", "<=", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 23:59:59'))
                    ]
            all_activity_domain += [
                       ("date_deadline", ">=", sd(today.replace(day=1))),
                       ("date_deadline", "<=", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 23:59:59'))
                    ]
        if date_val and date_val == 'current_year':
            lead_domain += [
                       ("date_deadline", ">=", sd(starting_of_year)),
                       ("date_deadline", "<=", sd(ending_of_year)),
                    ]
            
            lead_domain_query += [("c_lead.create_date >= %s"),("c_lead.create_date <= %s")]
            lead_domain_value=( sd(starting_of_year),
                                sd(ending_of_year)
                                )
            pipeline_domain_query += [("c_lead.date_deadline >= %s"),("c_lead.date_deadline <= %s")]
            
            new_customer_domain_query += [("create_date >= %s"),("create_date <= %s")]  
                    
            new_customer_domain += [
                       ("create_date", ">=", sd(starting_of_year)),
                       ("create_date", "<=", sd(ending_of_year)),
                    ]
            all_activity_domain += [
                       ("date_deadline", ">=", sd(starting_of_year)),
                       ("date_deadline", "<=", sd(ending_of_year)),
                    ]
        
        pipeline_domain_value = lead_domain_value
        new_customer_domain_value = lead_domain_value
#        ====================lead query data=======================
        and_lead_query=' AND '.join(lead_domain_query)
        if and_lead_query:
            lead_domain_value += ('lead',)
            final_lead_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id  \
                                where
                                """ + and_lead_query + ' and c_lead.type = %s' + ' ORDER BY create_date desc'
            
            self._cr.execute(final_lead_query, lead_domain_value) 
        else:
            final_lead_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id where c_lead.type = 'lead' ORDER BY create_date desc \
                                """
            self._cr.execute(final_lead_query)
        all_leads = self._cr.dictfetchall() 
        
        
        
#        =============pipline query data=================
        and_pipline_query=' AND '.join(pipeline_domain_query)
        if and_pipline_query:
            pipeline_domain_value += ('opportunity',)
            final_pipeline_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id  \
                                where
                                """ + and_pipline_query + ' and c_lead.type = %s' + ' ORDER BY create_date desc'
            self._cr.execute(final_pipeline_query, pipeline_domain_value)
        else:
            final_pipeline_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id where c_lead.type = 'opportunity' ORDER BY create_date desc \
                                """
            self._cr.execute(final_pipeline_query)
        my_pipeline = self._cr.dictfetchall() 
        
#        ======================================priority wise lead==================
        
        
        and_priority_lead_query=' AND '.join(lead_domain_query)
        
        if and_priority_lead_query:
            lead_domain_query += [("c_lead.type = %s"),("c_lead.priority = %s")]
            and_priority_lead_query = ' AND '.join(lead_domain_query)
            lead_priority_filter = vals.get('lead_priority_filter') or 0
            lead_domain_value += ('%s'%lead_priority_filter,)
            final_priority_lead_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id  \
                                where
                                """ + and_priority_lead_query +' ORDER BY probability desc'
            self._cr.execute(final_priority_lead_query, lead_domain_value) 
        else:
            lead_priority_filter = vals.get('lead_priority_filter') or 0
            priority_lead_domain_value = ('%s'%lead_priority_filter,)
            final_priority_lead_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id where c_lead.type = 'lead' \
                                and c_lead.priority = %s  ORDER BY probability desc 
                                """
            self._cr.execute(final_priority_lead_query,priority_lead_domain_value)
        priority_wise_all_leads = self._cr.dictfetchall()
        

#        ============================priority wise pipeline==========================================
        
        
        and_priority_pipline_query=' AND '.join(pipeline_domain_query)
        
        if and_priority_pipline_query:
            pipeline_domain_query += [("c_lead.type = %s"),("c_lead.priority = %s")] 
            and_priority_pipline_query=' AND '.join(pipeline_domain_query)
            
            pipeline_priority_filter = vals.get('pipeline_priority_filter') or 0
            pipeline_domain_value += ('%s'%pipeline_priority_filter,)
            
            
            final_priority_pipline_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id  \
                                where
                                """ + and_priority_pipline_query +' ORDER BY expected_revenue desc'
            self._cr.execute(final_priority_pipline_query, pipeline_domain_value) 
        else:
            pipeline_priority_filter = vals.get('pipeline_priority_filter') or 0
            pipeline_domain_value += ('%s'%pipeline_priority_filter,)
            final_priority_pipline_query = """SELECT c_lead.*,rp.name As partner_name,ct.name AS sale_team FROM crm_lead as c_lead \
                                join res_partner as rp on c_lead.partner_id = rp.id \
                                join crm_team as ct on c_lead.team_id = ct.id where c_lead.type = 'lead' \
                                and c_lead.priority = %s  ORDER BY expected_revenue desc 
                                """
            self._cr.execute(final_priority_pipline_query,pipeline_domain_value)
        priority_my_pipeline = self._cr.dictfetchall()
        

#        =============================new customer=======================
        
        and_new_customer_domain_query=' AND '.join(new_customer_domain_query)
        if and_new_customer_domain_query:
            final_new_customer_query = """SELECT id,name,mobile from res_partner where \
                                            """ + and_new_customer_domain_query + ' ORDER BY id desc'
            self._cr.execute(final_new_customer_query,new_customer_domain_value)
        else:
            final_new_customer_query = """SELECT id,name,mobile from res_partner """ + ' ORDER BY id desc'
            self._cr.execute(final_new_customer_query)
        
        new_customer_record = self._cr.dictfetchall()
        
        
        
        lost_lead = []     
        lost_lead += lead_domain
        lost_lead += [('active','=',False),('probability', '=', 0)]
        my_pipeline_domain += lead_domain
        lead_domain += [('type','=','lead'), ('type','=',False)]
        my_pipeline_domain += [('type','=','opportunity')]
        all_lost_lead = self.search_read(lost_lead,
                     fields=['name','partner_id','email_from','phone','user_id','team_id','date_deadline',
                     'priority','expected_revenue','stage_id','active','probability'],
                     order="date_deadline desc")
                     
#        all_leads = self.search_read(lead_domain,
#                     fields=['name','partner_id','email_from','phone','user_id','team_id','date_deadline',
#                     'priority','expected_revenue','stage_id','active','probability'],
#                     order="date_deadline desc")
#        print ("all_leads======",len(all_leads))
        
        p_lead_domain = []
        p_lead_domain += lead_domain
        p_lead_domain += [('priority','=',int(vals.get('lead_priority_filter') or 0))]
        
        p_pipeline_domain = []
        p_pipeline_domain += my_pipeline_domain
        p_pipeline_domain += [('priority','=',int(vals.get('pipeline_priority_filter') or 0))]
        
        
#        my_pipeline = self.search_read(my_pipeline_domain,
#                     fields=['name','partner_id','email_from','phone','user_id','team_id','date_deadline',
#                     'priority','expected_revenue','stage_id','active','probability'],
#                     order="date_deadline desc")
                     
         
        
        all_won_pipeline = []
        all_expected_revenue = []
        top_lost_customer = []
        for pipeline in my_pipeline:
            crm_stage = self.env['crm.stage'].browse(pipeline.get('stage_id'))
            if crm_stage.is_won:
                all_won_pipeline.append(pipeline)
            if not crm_stage.is_won:
                all_expected_revenue.append(pipeline)
            if (pipeline.get('active') == False and pipeline.get('probability') == 0):
                top_lost_customer.append(pipeline)
        
        
#        new_customer_record = self.env['res.partner'].search_read(new_customer_domain,
#                     fields=['name','mobile'],
#                     order="id desc")
        all_activity_domain += [('res_model','=','crm.lead')]
        all_activity = self.env['mail.activity'].search_read(all_activity_domain,
                     fields=['res_name','activity_type_id','summary','date_deadline','state','res_model','res_id'],
                     order="date_deadline desc")
         
         
#        =======================top won customer=====================
        top_won_customer_number_filter = int(vals.get('top_won_customer_filter') or 10 )
        top_five_won_customer = (sorted(all_won_pipeline, key=lambda i: i['expected_revenue'], reverse=True))[0:top_won_customer_number_filter] 
#        
        final_top_won_customer = []
        for won_customer in top_five_won_customer:
            final_top_won_customer.append({'label':won_customer.get('partner_name'),'y':won_customer.get('expected_revenue')})
        
        top_won_pipeline_chart_data = [
                                {'type':vals.get('top_won_customer_chart_type') or 'column',
                                'dataPoints':final_top_won_customer
                                }
                            ]
        top_won_customer_chart_type = 'Column'
        if vals.get('top_won_customer_chart_type'):
            top_won_customer_chart_type = vals.get('top_won_customer_chart_type').capitalize()
            
#        ===============================top sale team lead===========================================

        top_sale_team_pipeline_filter_number = int(vals.get('sale_team_opportunity_number') or 3 )
        for a_pipeline in my_pipeline:
            a_pipeline['team_id'] = a_pipeline.get('sale_team').get('en_US') or "Other"
        sale_team_pipeline_lines=sorted(my_pipeline,key=itemgetter('team_id'))
        sale_team_pipeline_groups = itertools.groupby(sale_team_pipeline_lines, key=operator.itemgetter('team_id'))
        sale_team_pipeline_lines = [{'team_id':k,'values':[x for x in v]} for k, v in sale_team_pipeline_groups] 
        f_sale_team_pipeline_data = []
        for s_team_pipeline_lines in sale_team_pipeline_lines:
            expected_revenue = sum([l.get('expected_revenue') for l in s_team_pipeline_lines.get('values')])
            f_sale_team_pipeline_data.append({'team_id':s_team_pipeline_lines.get('team_id'),'expected_revenue':expected_revenue})
        f_sale_team_pipeline_data_desc=sorted(f_sale_team_pipeline_data,key=itemgetter('expected_revenue'),reverse=True)[0:top_sale_team_pipeline_filter_number] 
        
        sale_team_pipeline_chart_record = []
        for sale_team_pipeline_data_desc in f_sale_team_pipeline_data_desc:
            sale_team_pipeline_chart_record.append({'label':sale_team_pipeline_data_desc.get('team_id'),
                                                'y':sale_team_pipeline_data_desc.get('expected_revenue')})
        top_sale_team_pipeline_chart_data = [
                                {'type':vals.get('top_sale_team_opportunity_chart') or 'column',
                                'dataPoints':sale_team_pipeline_chart_record
                                }
                            ]
        top_sale_team_pipeline_chart_type = 'Column'
        if vals.get('top_sale_team_opportunity_chart'):
            top_sale_team_pipeline_chart_type = vals.get('top_sale_team_opportunity_chart').capitalize()


#        ========================top expected revenue=====all_expected_revenue===================

        top_expected_revenue_number = int(vals.get('top_expected_revenue_number') or 5 )
        all_expected_revenue = (sorted(all_expected_revenue, key=lambda i: i['expected_revenue'], reverse=True))[0:top_expected_revenue_number] 
        all_expected_revenue_chart_record = []
        for a_expected_revenue in all_expected_revenue:
            all_expected_revenue_chart_record.append({'label':a_expected_revenue.get('partner_name') or 'Other',
                                                'y':a_expected_revenue.get('expected_revenue')})
        
        top_expected_revenue_chart_data = [
                                {'type':vals.get('top_expected_revenue_chart') or 'column',
                                'dataPoints':all_expected_revenue_chart_record
                                }
                            ]
        top_expected_revenue_chart_type = 'Column'
        if vals.get('top_expected_revenue_chart'):
            top_expected_revenue_chart_type = vals.get('top_expected_revenue_chart').capitalize()
            
#        ==================================top lost customer=========================================

        top_lost_chart_number_filter = int(vals.get('top_lost_chart_number_filter') or 5 )
        all_lost_lead = (sorted(all_lost_lead, key=lambda i: i['expected_revenue'], reverse=True))[0:top_lost_chart_number_filter] 
        all_lost_chart_record = []
        for a_lost_lead in all_lost_lead:
            all_lost_chart_record.append({'label':a_lost_lead.get('partner_id')and a_lost_lead.get('partner_id')[1] or 'Other',
                                                'y':a_lost_lead.get('expected_revenue')})
        
        top_lost_chart_data = [
                                {'type':vals.get('top_lost_chart_filter') or 'column',
                                'dataPoints':all_lost_chart_record
                                }
                            ]
        top_lost_chart_type = 'Column'
        if vals.get('top_lost_chart_filter'):
            top_lost_chart_type = vals.get('top_lost_chart_filter').capitalize()
            
#        =============================lead priority filter====================================

#        priority_wise_all_leads = self.search_read(p_lead_domain,
#                     fields=['name','partner_id','email_from','phone','user_id','team_id','date_deadline',
#                     'priority','expected_revenue','stage_id','active','probability'],
#                     order="probability desc")
                     
        priority_lead_chart_record = []
        for p_wise_all_leads in priority_wise_all_leads:
            priority_lead_chart_record.append({'label':p_wise_all_leads.get('partner_name') or 'Other',
                                                'y':p_wise_all_leads.get('probability')})
        
        priority_wise_lead_chart_data = [
                                {'type':vals.get('priority_lead_chart_filter') or 'column',
                                'dataPoints':priority_lead_chart_record
                                }
                            ]
        priority_wise_lead_chart_type = 'Column'
        if vals.get('priority_lead_chart_filter'):
            priority_wise_lead_chart_type = vals.get('priority_lead_chart_filter').capitalize()
        
        lead_priority_name = 'Low Priority'
        if vals.get('lead_priority_filter') == str(1):
            lead_priority_name = 'Medium Priority'
        if vals.get('lead_priority_filter') == str(2):
            lead_priority_name = 'High Priority'
        if vals.get('lead_priority_filter') == str(3):
            lead_priority_name = 'Very High Priority'
            
            
#        =================================Pipeline priority filter===================================
        
#        priority_my_pipeline = self.search_read(p_pipeline_domain,
#                     fields=['name','partner_id','email_from','phone','user_id','team_id','date_deadline',
#                     'priority','expected_revenue','stage_id','active','probability'],
#                     order="expected_revenue desc")
                     
        priority_pipeline_chart_record = [] 
        for p_wise_all_pipeline in priority_my_pipeline:
            crm_stage = self.env['crm.stage'].browse(p_wise_all_pipeline.get('stage_id'))
            if not crm_stage.is_won:
                priority_pipeline_chart_record.append({'label':p_wise_all_pipeline.get('partner_name') or 'Other',
                                                'y':p_wise_all_pipeline.get('expected_revenue')})
        
        priority_wise_pipeline_chart_data = [
                                {'type': vals.get('priority_pipeline_chart_filter') or 'column',
                                'dataPoints':priority_pipeline_chart_record
                                }
                            ]
        
        priority_wise_pipline_chart_type = 'Column'
        if vals.get('priority_pipeline_chart_filter'):
            priority_wise_pipline_chart_type = vals.get('priority_pipeline_chart_filter').capitalize()
            
        pipeline_priority_name = 'Low Priority'
        if vals.get('pipeline_priority_filter') == str(1):
            pipeline_priority_name = 'Medium Priority'
        if vals.get('pipeline_priority_filter') == str(2):
            pipeline_priority_name = 'High Priority'
        if vals.get('pipeline_priority_filter') == str(3):
            pipeline_priority_name = 'Very High Priority'
            
        final_all_activity = all_activity
        final_upcoming  = []
        for a_activity in all_activity:
            if a_activity.get('date_deadline') >= date.today():
                final_upcoming.append(a_activity)
            a_activity['date_deadline'] = a_activity.get('date_deadline').strftime('%d-%m-%Y')
        
        return {
            'all_leads':all_leads,
            'my_pipeline':my_pipeline,
            'all_won_pipeline':all_won_pipeline,
            'new_customer_record':new_customer_record,
            'all_activity':final_all_activity,
            'list_all_activity':final_all_activity[0:10],
            'upcoming_activity':final_upcoming[0:5],
            'all_leads_list':all_leads[0:10],
            'my_pipeline_list':my_pipeline[0:10],
            'won_pipeline_chart_data':top_won_pipeline_chart_data,
            'won_pipeline_chart_type':top_won_customer_chart_type,
            'top_won_customer_number_filter':top_won_customer_number_filter, 
            'top_sale_team_pipeline_chart_data':top_sale_team_pipeline_chart_data,
            'top_sale_team_pipeline_chart_type':top_sale_team_pipeline_chart_type,
            'top_sale_team_pipeline_filter_number':top_sale_team_pipeline_filter_number, 
            'top_expected_revenue_chart_data':top_expected_revenue_chart_data,
            'top_expected_revenue_number':top_expected_revenue_number,
            'top_expected_revenue_chart_type':top_expected_revenue_chart_type,
            'top_lost_chart_data':top_lost_chart_data,
            'top_lost_chart_number_filter':top_lost_chart_number_filter,
            'top_lost_chart_type':top_lost_chart_type,
            'priority_wise_lead_chart':priority_wise_lead_chart_data,
            'priority_wise_lead_chart_type':priority_wise_lead_chart_type,
            'lead_priority_name':lead_priority_name,
            
            'priority_wise_pipeline_chart_data':priority_wise_pipeline_chart_data,
            'priority_wise_pipline_chart_type':priority_wise_pipline_chart_type,
            'pipeline_priority_name':pipeline_priority_name,
            
        }
    
    @api.model
    def load_users_and_partners(self):
        
        return{
               'partners': self.env['res.partner'].sudo().search_read([],['name']),
               'users': self.env['res.users'].sudo().search_read([],['name']),
            }
    
    def action_activity_mark_as_done(self):
        res = self.action_done()
        return res

#    def action_print_excel_report(self):
#        print ("self======",self)
#        print ("self======",self._context)
#        return True
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
