# __manifest__.py
{
    'name': 'Set Invoice Date to Today',
    'version': '1.1',
    'summary': 'Automatically sets the invoice date to today\'s date in account.move',
    'description': 'This module sets the invoice date to today\'s date whenever an invoice is created or updated.',
    'author': 'Loai Souboh',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [],
    'installable': True,
    'application': False,
}
