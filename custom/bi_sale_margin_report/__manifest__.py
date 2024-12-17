# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Sales Margin Reports(PDF/Excel) in Odoo",
    "version" : "16.0.0.0",
    "category" : "Sales",
    'summary': 'Sale Margin Report sale profit analysis for product margin excel report sale margin excel report sale margin xls report invoice margin report Margin cost Analysis report quotation margin report margin on product margin analysis report margin percentage',
    'description': """

    Odoo sales margin report sale margin pdf report sale margin analysis report
    Odoo margin calculation report sales margin pdf report sales margin analysis report
    Odoo invoice margin report invoice margin analysis report
    BrowseInfo developed a new odoo/OpenERP module apps.
    This module use for 
    odoo calculate margin on product margin on sales margin on invoice Shows total margin on orders reports
    Odoo shows margin on sale order line Calculate margin on percentage and fixed sales Margin Analysis report
    odoo Margin on Product, Sale and Invoice margin by percentage margin in invoice margin fix amount report 
    Odoo margin in SO margin in bill margin on sales order line margin in sales order line
    odoo calculate margin by pecentage add margin on invoice and product add margin on cost price margin cost price 
    odoo margin report in cost odoo sales margin report sales
    odoo margin on Sales Analysis Report margin on Invoices Analysis Repor  INVOICE COST MARGIN REPORT 
    odoo Print Invoice cost margin Excel report margin in view quotation sale and invoice
    Odoo product cost margin sales cost margin sales order cost margin calculate Margin cost Analysis  
    Odoo Margin cost Analysis report Print sales margin report in excel print sales margin report in pdf
    
   
Este módulo se usa para calcular el margen en el producto, margion en las ventas, margen en la factura. Muestra el margen total en los pedidos.
también muestra el margen en la línea de orden de venta. Calcula el margen en porcentaje y fijo. Análisis de Margen, Margen en Producto, Venta y Factura.Ce module est utilisé pour calculer la marge sur le produit, la marge sur les ventes, la marge sur la facture. Affiche la marge totale sur les commandes.
montre également la marge sur la ligne de commande de vente. Calculer la marge sur le pourcentage et fixe. Analyse de marge, marge sur le produit, vente et facture
Dieses Modul wird für die Berechnung der Marge auf Produkt, Marge auf Umsatz, Marge auf Rechnung verwendet. Zeigt die Gesamtmarge für Bestellungen an.
zeigt auch die Marge aus der Verkaufsauftragszeile an. Berechne Marge auf Prozentsatz und reparierte. Margin Analyse, Margin auf Produkt, Verkauf und RechnungGebruik deze module voor het berekenen van de marge op het product, de marge op de verkoop, de marge op de factuur. Toont de totale marge op bestellingen.
toont ook marge op verkooporderregel. Bereken marge op percentage en fixed.Margin Analysis, Margin on Product, Sale and Invoice

Este módulo usa para calcular a margem no produto, a margem nas vendas, a margem na fatura. Mostra a margem total em pedidos.
também mostra margem na linha de ordem de venda. Calcular a margem em porcentagem e fixo.Análise de margem, margem sobre produto, venda e fatura
تستخدم هذه الوحدة لحساب الهامش على المنتج ، والهامش على المبيعات ، والهامش على الفاتورة. يعرض إجمالي الهامش على الطلبات.
كما يظهر هامش على طلب بيع الخط. حساب الهامش على النسبة المئوية والثابتة. تحليل المارجن ، الهامش على المنتج ، البيع والفاتورة
tustakhdam hadhih alwahdat lihisab alhamish ealaa almuntaj , walhamish ealaa almubieat , walhamish ealaa alfaturat. yuearid 'iijmalia alhamish ealaa altalabat.
kama yuzhir hamish ealaa talab baye alkhuta. hisab alhamish ealaa alnisbat almiawiat walththabita. tahlil almarijin , alhamish ealaa almuntaj , albaye walfatur

Este módulo se usa para calcular el margen en el producto, margion en las ventas, margen en la factura. Muestra el margen total en los pedidos.
también muestra el margen en la línea de orden de venta. Calcula el margen en porcentaje y fijo. Análisis de Margen, Margen en Producto, Venta y Factura.

 With Sales margin Odoo apps, you can measure sales margin of your company. Sales Margin scale will help company management to measure progress in the sales and marketing section. In this profit margin report, you can see a profit margin of each sales order. In this report, you can get more information like cost,untaxed amount, discount and margin percentage. To get specific data from the large data there are many options available like company, warehouses, sales channel, sales person, customer, products. In this app, there is a feature if you want to identify sales order in which the margin is negative.

    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    "price": 69,
    "currency": 'EUR',
    "depends" : ['base','sale_management','stock','sale_stock'],
    "data": ['security/ir.model.access.csv',
            'wizard/sale_margine_wizard.xml',
            'report/sales_margin_report.xml',
            'report/report_views.xml',
        ],
    'qweb': [
    ],
    "license":'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/sS8jiTKrTRc',
    "images":["static/description/Banner.gif"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
