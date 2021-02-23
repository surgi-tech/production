from odoo import fields, models, api, exceptions
from odoo import SUPERUSER_ID


class NewModule(models.TransientModel):
    _name = 'wizard.po.open'
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="", required=False, )
    def create_po(self):
        print('ffffffff')
        lines_list=[]
        # self.env['purchase.order'].create({'name':'Salah'})
        stock = self.env['stock.quant'].browse(self._context.get('active_ids', []))
        print(stock,'DDDDDDDDDDDDDDDDDD')
        for rec in stock:
            lines_list.append((0,0,{
                'product_id':rec.product_id.id,
                'name':rec.product_id.name,
                'product_qty':rec.quantity,

            }))
        self.env['purchase.order'].create({'company_id':self.company_id.id,'name':'Stock Quant','partner_id':self.partner_id.id,'order_line':lines_list})


class stock_quant_inherit_wizard(models.Model):
    _inherit = 'stock.quant'

    is_operation_related = fields.Boolean(related="location_id.is_operation_location",
                                          string="Is Operation Location",store=True)
    is_operation_freeze = fields.Boolean(related="location_id.operation_location_freeze",
                                          string="Is Operation Location Freeze",store=True)

    def open_wizard_stock(self):
        action = self.env.ref('stock_quant.action_wizard_stock_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_line_stock_quant', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'current'
        return result

    def open_wizard_back_to_warehouse(self):
        action = self.env.ref('stock_quant.action_wizard_back_to_warehouse_quant')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_back_to_warehouse', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result


    def open_wizard_create_po(self):
        self = self.with_user(SUPERUSER_ID)

        return {
            'name': "Operations Quantities",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'field_parent': 'child_ids',
            'res_model': 'purchase.order',
            'target': 'new',
            # 'domain': [('id', 'in', list)],
        }






    def open_wizard_move_to_location(self):
        action = self.env.ref('stock_quant.action_wizard_wizard_move_to_location')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_wizard_move_to_location', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    def open_wizard_move_to_hanged_warehouse(self):
        action = self.env.ref('stock_quant.action_wizard_wizard_move_to_hanged_warehouse')
        result = action.read()[0]
        res = self.env.ref('stock_quant.wizard_wizard_move_to_hanged_warehouse', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result
