# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiApplayJob(http.Controller):
#     @http.route('/surgi_applay_job/surgi_applay_job/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_applay_job/surgi_applay_job/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_applay_job.listing', {
#             'root': '/surgi_applay_job/surgi_applay_job',
#             'objects': http.request.env['surgi_applay_job.surgi_applay_job'].search([]),
#         })

#     @http.route('/surgi_applay_job/surgi_applay_job/objects/<model("surgi_applay_job.surgi_applay_job"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_applay_job.object', {
#             'object': obj
#         })
