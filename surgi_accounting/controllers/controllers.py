# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiAccounting(http.Controller):
#     @http.route('/surgi_accounting/surgi_accounting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_accounting/surgi_accounting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_accounting.listing', {
#             'root': '/surgi_accounting/surgi_accounting',
#             'objects': http.request.env['surgi_accounting.surgi_accounting'].search([]),
#         })

#     @http.route('/surgi_accounting/surgi_accounting/objects/<model("surgi_accounting.surgi_accounting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_accounting.object', {
#             'object': obj
#         })
