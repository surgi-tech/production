
from odoo import models ,fields

class product_line(models.Model):
    _name = 'product.operation.line'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    operation_id = fields.Many2one('operation.operation')
    picking_id = fields.Many2one('stock.picking')
