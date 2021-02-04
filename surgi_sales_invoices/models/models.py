# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class surgi_sales_invoices(models.Model):
#     _name = 'surgi_sales_invoices.surgi_sales_invoices'
#     _description = 'surgi_sales_invoices.surgi_sales_invoices'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
