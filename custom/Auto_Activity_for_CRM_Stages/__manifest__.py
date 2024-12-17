{
    'name': 'Auto Activity for CRM Stages',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Automatically create activities for CRM stages',
    'description': 'This module creates activities for CRM stages automatically based on configuration.',
    'author': 'Loai Souboh',
    'depends': ['crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_stage_views.xml',
        'views/auto_activity_config_views.xml',
    ],
    'installable': True,
    'application': False,
}
