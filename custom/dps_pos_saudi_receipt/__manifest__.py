{
    'name': 'POS Arabic Receipt | POS Saudi Arabic Receipt | POS Electronic invoice with barcode in POS',
    'version': '15.1.1.1',
    'sequence': 1,
    'email': 'dotsprime@gmail.com',
    # 'website':'http://dotsprime.com/',
    'category': 'Point of Sale',
    'summary': 'POS Electronic invoice with barcode in POS',
    'author': 'DOTSPRIME',
    'price': 15,
    'currency': 'USD',
    'license': 'OPL-1',
    'description': """
    POS Customized Receipt, POS Electronic invoice with barcode in POS.
        """,
    "live_test_url" : "",
    'depends': ['point_of_sale','pos_restaurant','l10n_gcc_pos','l10n_sa_pos','l10n_co_pos','sh_pos_all_in_one_retail'],
    'data': ['views/product_view.xml'],
    'images': ['static/description/main_screenshot.jpg'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'point_of_sale.assets': [
            'dps_pos_saudi_receipt/static/src/css/arabic_font.css',
            'dps_pos_saudi_receipt/static/src/js/JsBarcode.all.min.js',
            'dps_pos_saudi_receipt/static/src/js/models.js',
            'dps_pos_saudi_receipt/static/src/js/OrderReceipt.js',            
            'dps_pos_saudi_receipt/static/src/xml/templates.xml',
        ],
        'web.assets_qweb': [
            'dps_pos_saudi_receipt/static/src/xml/templates.xml',
        ],
    },    
}
