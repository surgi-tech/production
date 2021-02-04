# -*- coding: utf-8 -*-
# from odoo import http


# class SurgiSalesInvoices(http.Controller):
#     @http.route('/surgi_sales_invoices/surgi_sales_invoices/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/surgi_sales_invoices/surgi_sales_invoices/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('surgi_sales_invoices.listing', {
#             'root': '/surgi_sales_invoices/surgi_sales_invoices',
#             'objects': http.request.env['surgi_sales_invoices.surgi_sales_invoices'].search([]),
#         })

#     @http.route('/surgi_sales_invoices/surgi_sales_invoices/objects/<model("surgi_sales_invoices.surgi_sales_invoices"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('surgi_sales_invoices.object', {
#             'object': obj
#         })
