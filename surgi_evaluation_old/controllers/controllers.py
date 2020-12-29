# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSurveys(http.Controller):
#     @http.route('/surgi_evaluation/surgi_evaluation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_evaluation/surgi_evaluation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_evaluation.listing', {
#             'root': '/surgi_evaluation/surgi_evaluation',
#             'objects': http.request.env['surgi_evaluation.surgi_evaluation'].search([]),
#         })

#     @http.route('/surgi_evaluation/surgi_evaluation/objects/<model("surgi_evaluation.surgi_evaluation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_evaluation.object', {
#             'object': obj
#         })
