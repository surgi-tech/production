from odoo import fields, models, api, exceptions


class stock_quant_inherit_wizard(models.Model):
    _inherit = 'stock.quant'

    @api.depends('location_id.warehouse_id.warehouse_users')
    def _get_wh_user(self):
        for obj in self:
            for user in obj.location_id.warehouse_id.warehouse_users:
                if(self.env.user.id == user.id):
                    obj.is_wh_user=True
                    break
                print ("WH result: ",obj.is_wh_user)

    def _get_is_hanged(self):
        for obj in self:
            dist_warehouse = self.env['stock.warehouse'].search([('is_hanged_warehouse', '=', True)])
            location = self.env['stock.location'].search(
                [('warehouse_id', '=', dist_warehouse.id), ('is_operation_location', '=', True),
                 ('usage', '=', 'internal')])
            obj.is_hanged = (obj.location_id.id == location.id)


    is_wh_user = fields.Boolean(default=False, compute=_get_wh_user,store=True)
    is_hanged = fields.Boolean(default=False, compute=_get_is_hanged)
    operation_location_id = fields.Many2one('stock.location', string="Operation Location", readonly=True)

class stock_hanged_quant_inherit(models.Model):
    _name = 'hanged.stock.quant'
    _inherit = 'stock.quant'

    quant_id = fields.Many2one('stock.quant', readonly=True)
    invoice_id = fields.Many2one(comodel_name='account.move', string='Invoice', readonly=True)
    operation_id=fields.Many2one('operation.operation',string="Operation", readonly=True)

    def open_wizard_hanged_move_to_hanged_warehouse(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_back_to_warehouse_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_back_to_warehouse', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    def open_wizard_hanged_delivery(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_delivery_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_delivery', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    def open_wizard_hanged_invoice(self):
        action = self.env.ref('stock_quant.action_wizard_hanged_invoice_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_hanged_invoice_stock_quant', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result