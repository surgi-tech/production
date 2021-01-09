# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiHrGroups(http.Controller):
#     @http.route('/surgi_hr_groups/surgi_hr_groups/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_hr_groups/surgi_hr_groups/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_hr_groups.listing', {
#             'root': '/surgi_hr_groups/surgi_hr_groups',
#             'objects': http.request.env['surgi_hr_groups.surgi_hr_groups'].search([]),
#         })

#     @http.route('/surgi_hr_groups/surgi_hr_groups/objects/<model("surgi_hr_groups.surgi_hr_groups"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_hr_groups.object', {
#             'object': obj
#         })
