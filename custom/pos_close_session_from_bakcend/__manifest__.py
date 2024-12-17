# See LICENSE file for full copyright and licensing details.
{
    "name": "POS Close Session From Backend",
    "version": "16.0.0.1",
    "category": "Point of Sale",
    "author": "TechUltra Solutions Private Limited",
    "website": "www.techultrasolutions.com",
    "summary": """ Odoo base allows you to close a session and post a journal entry from within the POS software, 
                   however it might be time consuming to open the POS app for each shop just to post a journal entry. \
                   To address this issue, we created an app that allows you to close and submit journal entries outside of the POS apps. Scroll below to know its functionality.""",
    "description": """
                Odoo base allows you to close a session and post a journal entry from within the POS software, however it might be time consuming to open the POS app for each shop just to post a journal entry. To address this issue, we created an app that allows you to close and submit journal entries outside of the POS apps. Scroll below to know its functionality.
    """,
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/close_session_wizard.xml",
        "views/pos_session_view_inherit.xml",
    ],
    "images": [
        "static/description/main_screen.gif",
    ],
    "currency": "USD",
    "price": 25,
    "application": False,
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}
