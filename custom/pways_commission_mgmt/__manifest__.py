# -*- coding: utf-8 -*-

{
    "name" : "Commission Management System",
    "version" : "15.0",
    'category' : "Sales",
    "summary" : """Commission for salesperson, salesteam or agents , based on partner, product, product category and calculated on sales or invoice or payment confirmation on specific rates
                    Sales Commission
                    Invoice Commission
                    Payment Commission
                    Partner Commission
                    Partner Referral 
                    Partner Incentive
                    Bonus Commission Pay.
                    Salary Plus Commission Pay. 
                    Variable Commission Pay 
                    Graduated Commission Pay
                    Residual Commission Pay 
                    Draw Against Commission Pay.
                    Base rate only commission. 
                    Base salary plus commission
                    Draw against a commission
                    Gross margin commission
                    Residual commission
                    Revenue commission
                    Straight commission
                    Tiered commission
                """,

    "description": "Commission for salesperson, salesteam or agents,  based on partner, product, product category and calculated on sales or invoice or payment confirmation on specific rates",
    'author':'Preciseways',
    'website': "http://www.preciseways.com",
    "depends" : ['sale_management', 'sale_stock',],
    "data" :[
        'view/sales_commission_security.xml',
        'security/ir.model.access.csv',
        'view/account_invoice_view.xml',
        'view/commission_view.xml',
        'view/res_partner_view.xml',
        'view/sale_config_settings.xml',
        'view/sale_view.xml',
        'report/commission_report.xml',
        'report/sale_inv_comm_template.xml'
    ],
    'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'price': 35,
    'currency': 'EUR',
    'license': 'OPL-1',
}
