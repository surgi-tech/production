# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesTraking(http.Controller):
#     @http.route('/surgi_sales_tracking/surgi_sales_tracking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_tracking/surgi_sales_tracking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_tracking.listing', {
#             'root': '/surgi_sales_tracking/surgi_sales_tracking',
#             'objects': http.request.env['surgi_sales_tracking.surgi_sales_tracking'].search([]),
#         })

#     @http.route('/surgi_sales_tracking/surgi_sales_tracking/objects/<model("surgi_sales_tracking.surgi_sales_tracking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_tracking.object', {
#             'object': obj
#         })
