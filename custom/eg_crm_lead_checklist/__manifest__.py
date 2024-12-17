{
    "name": "Checklist of CRM Lead",

    'version': "16.0",

    'category': "CRM",

    "summary": "This app will display custom stages and progressbar in percentage according to stages complate",

    'author': 'INKERP',

    'website': "https://www.INKERP.com",

    "depends": ['crm'],

    "data": [
        "views/crm_lead_form.xml",
        "views/crm_checklist_view.xml",
        "security/ir.model.access.csv"

    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
