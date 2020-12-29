from odoo import fields,api,models,exceptions

class stock_picking_type_inherit(models.Model):
    _inherit = 'stock.picking.type'

    surgeries_supply = fields.Boolean(string="Surgeries Supply")
