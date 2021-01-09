# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning

## Zienab Morsy Code Start ---->

class InitialDemand(models.Model):
    _name = 'initial.demand'


    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Integer(string='Quantity', required=True, default=1)
    pick_id = fields.Many2one('stock.picking')