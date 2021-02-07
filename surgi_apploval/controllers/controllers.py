# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiApploval(http.Controller):
#     @http.route('/surgi_apploval/surgi_apploval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_apploval/surgi_apploval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_apploval.listing', {
#             'root': '/surgi_apploval/surgi_apploval',
#             'objects': http.request.env['surgi_apploval.surgi_apploval'].search([]),
#         })

#     @http.route('/surgi_apploval/surgi_apploval/objects/<model("surgi_apploval.surgi_apploval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_apploval.object', {
#             'object': obj
#         })
