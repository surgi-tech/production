# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiTrust(http.Controller):
#     @http.route('/surgi_trust/surgi_trust/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_trust/surgi_trust/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_trust.listing', {
#             'root': '/surgi_trust/surgi_trust',
#             'objects': http.request.env['surgi_trust.surgi_trust'].search([]),
#         })

#     @http.route('/surgi_trust/surgi_trust/objects/<model("surgi_trust.surgi_trust"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_trust.object', {
#             'object': obj
#         })
