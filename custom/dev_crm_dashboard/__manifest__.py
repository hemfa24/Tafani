# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'CRM Dashboard, Lead-Customer-Pipeline Activities graph Filter Dashbaord',
    'version': '16.0.1.0',
    'sequence': 1,
    'category': 'Tools',
    'description':
        """
   Odoo application introduces a comprehensive CRM Dashboard, seamlessly integrating various lead and pipeline management functions into a unified platform. With this tool, you gain convenient access to all your leads and pipelines from diverse sources, simplifying your workflow. The Dashboard offers a rich array of data visualization options through an assortment of charts, enhancing your understanding of your business's performance. Customizable filters enable you to effortlessly organize and retrieve leads and pipelines by user, customer, and date, with the added flexibility of specifying precise date ranges. Additionally, you can easily monitor associated activities and stay ahead of your schedule with the upcoming activities panel. The Dashboard further empowers you with insightful charts, such as Won Customer, Team Pipeline, Expected Revenue, Lost Customer, Lead Low Priority, and Pipeline Low Priority, all supported by user-friendly top 10, 20, and other filter options. Elevate your CRM experience with this robust and intuitive tool. 
   
   Dashboard for centralizing access to all leads and pipelines in one location
 Upcoming activities notification panel
 Access All Activities as list on the dashboard
 View activity from list
 View document of the activity from list
 Access Lead as list on the dashboard
 View Lead from the list
 Access Pipeline as list on the dashboard
 View Pipeline from the list
 Here, you have access to a variety of simple yet effective data filtering options
    Top Won Customer
    Top Sale Team Pipeline
    Top Expected Revenue
    Top Lost Customers
    Top Lead Low Priority
    Top Pipeline Low Priority
 All above are available in below charts:
    Column Chart
    Pie Chart
    Line Chart
    Doughnut Chart
    Line Area Chart
    Scatter Chart
    Bar Chart
 When using the Top Priority filter, consider the following
    Low Priority
    Medium Priority
    High Priority
    Very High Priority
 In other filter, consider the following
    Top 5
    Top 10
    Top 15
    Top 20
    Top 25
 Filter overall records by:

    User
    Customer
    Date

 Date filters are:

    Today
    All
    Yesterday
    This Week
    Last Seven Days
    Last Week
    This Month
    This Year

 You can also select custom date range for the date filter 
 
 CRM Dashboard with building block and cool graph & list view, Total count of leads, pipelines, total customer in dashbaord, top customer dashboard, Top sales team dashbaord,List of activities, upcoming activities, Lead pipelines list, Expected revenue,Lost Customer, Priority chart, date user filters chart dashboard, crm sales dashboard, lead dashboard in odoo, salesteam crm dashbaord

    """,
    'summary': 'CRM Dashboard with building block and cool graph & list view, Total count of leads, pipelines, total customer in dashbaord, top customer dashboard, Top sales team dashbaord,List of activities, upcoming activities, Lead pipelines list, Expected revenue,Lost Customer, Priority chart, date user filters chart dashboard, crm sales dashboard, lead dashboard in odoo, salesteam crm dashbaord',
    'depends': ['crm', 'mail'],
    'data': [
        'views/dashboard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dev_crm_dashboard/static/src/css/dashboard_new.css',
            'dev_crm_dashboard/static/src/js/main.js',
            'dev_crm_dashboard/static/src/js/canvasjs.min.js',
            'dev_crm_dashboard/static/src/xml/dashboard.xml'
        ],
    },
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':39.0,
    'currency':'EUR',
   # 'live_test_url':'https://youtu.be/TAwMhy000wM',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
