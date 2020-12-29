from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class product_tool_line(models.Model):
    _name = 'product.tool.line'
    # _rec_name = 'product_id'

    quantity = fields.Float('Quantity', required=True, default=1.0,)
    product_id = fields.Many2one('product.template','Product',ondelete='cascade',required=True,)

