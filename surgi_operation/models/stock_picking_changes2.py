# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

## Zienab Morsy Code Start ---->

# class StockMoveInherit(models.Model):
#     _inherit = 'stock.move'
#
#     def _action_confirm(self, merge=True, merge_into=False):
#         for move in self:
#             if not move.picking_id.is_operation_move:
#                return super(StockMoveInherit, self)._action_confirm()
#             else:
#                 move.state = 'waiting'
#         return self

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    is_operation_move = fields.Boolean(default=False)

    def get_intial_lines(self):
        data_lines = {}
        data_lines_keys = []
        for pack_operation in self.move_lines:
            if pack_operation.product_id.default_code :
                product= '['+ pack_operation.product_id.default_code +'] '+pack_operation.product_id.name
            else :
                product = pack_operation.product_id.name
            product_group = ''
            if pack_operation.product_group != False:
                if pack_operation.product_group.strip() != '':
                    product_group = pack_operation.product_group.strip()
            if product_group in data_lines.keys():
                data_lines[product_group].append({
                    'product_id': product,
                    'product_group': product_group,
                    'product_uom_qty': pack_operation.product_uom_qty,
                    'qty_done': pack_operation.quantity_done,
                    'delivery_difff': pack_operation.delivery_difff,
                    'product_uom_id': pack_operation.product_uom.name,
                })
            else:
                data_lines[product_group] = [{
                    'product_id': product,
                    'product_group': product_group,
                    'product_uom_qty': pack_operation.product_uom_qty,
                    'qty_done': pack_operation.quantity_done,
                    'delivery_difff': pack_operation.delivery_difff,
                    'product_uom_id': pack_operation.product_uom.name,
                }]
                data_lines_keys.append(product_group)
        final_lines = []
        for key in data_lines_keys:
            for data_line in data_lines[key]:
                final_lines.append(data_line)
        return final_lines

## Ahmed Salama Code End.

