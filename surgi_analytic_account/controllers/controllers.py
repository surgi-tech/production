# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiAnalyticAccount(http.Controller):
#     @http.route('/surgi_analytic_account/surgi_analytic_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_analytic_account/surgi_analytic_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_analytic_account.listing', {
#             'root': '/surgi_analytic_account/surgi_analytic_account',
#             'objects': http.request.env['surgi_analytic_account.surgi_analytic_account'].search([]),
#         })

#     @http.route('/surgi_analytic_account/surgi_analytic_account/objects/<model("surgi_analytic_account.surgi_analytic_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_analytic_account.object', {
#             'object': obj
#         })
