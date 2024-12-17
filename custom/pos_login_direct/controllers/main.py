# -*- coding: utf-8 -*
from odoo.http import request
from odoo import http, _
from odoo.osv.expression import AND
from odoo.addons.portal.controllers.web import Home
from odoo.addons.point_of_sale.controllers.main import PosController

import logging

_logger = logging.getLogger(__name__)

class PosHome(Home):

    @http.route()
    def web_login(self, *args, **kw):
        response = super(PosHome, self).web_login(*args, **kw)
        if request.session.uid:
            _logger.info('web_login ......................')
            user = request.env['res.users'].sudo().browse(request.session.uid)
            pos_config = user.pos_config_id
            if pos_config:
                return request.redirect('/pos/ui?config_id=%s' % pos_config.id)
        return response

class PosLoginDirectController(PosController):

    @http.route(['/pos/web', '/pos/ui'], type='http', auth='user')
    def pos_web(self, config_id=False, **k):

        domain = [
            ('state', 'in', ['opening_control', 'opened']),
            ('user_id', '=', request.session.uid),
            ('rescue', '=', False)
        ]
        if config_id:
            domain = AND([domain, [('config_id', '=', int(config_id))]])
        pos_session = request.env['pos.session'].sudo().search(domain, limit=1)
        if not pos_session and config_id:
            domain = [
                ('state', 'in', ['opening_control', 'opened']),
                ('rescue', '=', False),
                ('config_id', '=', int(config_id)),
            ]
            pos_session = request.env['pos.session'].sudo().search(domain, limit=1)
        user = request.env['res.users'].browse(request.session.uid)
        if not pos_session and config_id and user.pos_login_direct and user.pos_config_id and user.pos_config_id.id == int(config_id):
            request.env['pos.session'].create({'user_id': request.session.uid, 'config_id': int(config_id)})
        return super(PosLoginDirectController, self).pos_web(config_id=config_id, **k)