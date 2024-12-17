{
    "name": "HEMFA Sale Order Plan",
    "version": "16.0.1.0.1",
    "category": "Sales Management",
    "author": "HEMFA - E.Mudathir",
    'summary': """
       200_hemfa_sale_plan_R_D_16.0.0.1_2023.05.11
       Sale Order Plan by lot number / by sales person by/ customer 
         """,
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "stock_restrict_lot"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
    "view/sale_view.xml",
    "view/sale_plan_view.xml",],
    
    
    "installable": True,
}
