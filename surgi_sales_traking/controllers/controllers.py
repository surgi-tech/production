# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesTraking(http.Controller):
#     @http.route('/surgi_sales_traking/surgi_sales_traking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_traking/surgi_sales_traking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_traking.listing', {
#             'root': '/surgi_sales_traking/surgi_sales_traking',
#             'objects': http.request.env['surgi_sales_traking.surgi_sales_traking'].search([]),
#         })

#     @http.route('/surgi_sales_traking/surgi_sales_traking/objects/<model("surgi_sales_traking.surgi_sales_traking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_traking.object', {
#             'object': obj
#         })
