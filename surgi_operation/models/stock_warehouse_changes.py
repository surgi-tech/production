from odoo import fields,models,api
from odoo.fields import Datetime
from odoo.exceptions import Warning


class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    notifications = fields.Text(string='Notification Email/s')
    is_hanged_warehouse = fields.Boolean("Is Hanged Warehouse", default=False)

    @api.model
    def create(self, vals):
        if 'is_hanged_warehouse' in vals and vals['is_hanged_warehouse'] == True:
            existing_hanged_warehouses = self.env['stock.warehouse'].search([('is_hanged_warehouse','=',True)])
            existing_hanged_warehouses.write({
                'is_hanged_warehouse': False
            })
        res = super(stock_warehouse, self).create(vals)
        return res

    def write(self, vals):
        if 'is_hanged_warehouse' in vals and vals['is_hanged_warehouse'] == True:
            existing_hanged_warehouses = self.env['stock.warehouse'].search([('is_hanged_warehouse','=',True)])
            existing_hanged_warehouses.write({
                'is_hanged_warehouse': False
            })
        res = super(stock_warehouse, self).write(vals)
        return res