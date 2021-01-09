from odoo import models, fields, api,_
class ProductLines(models.Model):
    _name = 'product.lines'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()
    product_line = fields.Char(string="Parent Product Line")
