# -*- coding: utf-8 -*-
{
    'name': 'All In One WhatsApp Odoo Integration',
    'version': '16.0.1.2.2',
    'category': 'Tools',
    'author': 'InTechual Solutions',
    'license': 'OPL-1',
    'summary': '800_whatsapp_all_in_one_R_S_R16.0.1.0.1_18-5-2023 - All in One WhatsApp Integration with Odoo',
    'description': """
This module can be used to send messages to WhatsApp
----------------------------------------------------
Send Messages via WhatsApp
WhatsApp All in One Module
""",
    'depends': ['base', 'base_setup', 'contacts', 'account', 'sale_management', 'purchase', 'delivery', 'website_sale', 'point_of_sale'],
    'data': [
        'data/pos_receipt_paper_format.xml',
        'data/whatsapp_cron.xml',
        'data/wp_sequence.xml',
        'security/ir.model.access.csv',
        'wizard/send_wp_msg_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_inovice_form_wa_inherited.xml',
        'views/account_payment_form_wa_inherited.xml',
        'views/pos_config_views.xml',
        'views/purchase_order_form_wa_inherited.xml',
        'views/sale_order_form_wa_inherited.xml',
        'views/stock_picking_form_wa_inherited.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'whatsapp_all_in_one/static/src/js/views/many2many_tags_mobile.js',
            'whatsapp_all_in_one/static/src/js/views/many2many_tags_mobile.xml',
            'whatsapp_all_in_one/static/src/js/refresh_qr_code.js',
        ],
        'point_of_sale.assets': [
            'whatsapp_all_in_one/static/src/js/Screens/WhatsAppReceiptScreen.js',
            'whatsapp_all_in_one/static/src/js/Screens/WhatsAppReceiptScreen.xml',
            'whatsapp_all_in_one/static/src/js/Screens/popup.js',
            'whatsapp_all_in_one/static/src/js/Screens/popup.xml',
        ],
    },
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 1,
    'currency': 'EUR',
    'price': 30,
}
