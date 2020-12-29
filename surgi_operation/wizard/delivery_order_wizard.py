from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError, Warning


class wizard_stock_quant(models.TransientModel):
    _name = "wizard_stock_quant"

    # here we get data from selected lines and show it into wizard
    @api.model
    def get_stock_quant_lines(self):
        stock_active_ids = self._context.get('active_ids')
        stock_ids = self.env['stock.quant'].browse(stock_active_ids)

        dict = []
        for stk in stock_ids:
            for line in stk:
                res = self.env['stock.quant.items'].create({
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'quantity_moved': line.quantity,
                    'location_id': line.location_id.id,
                    'lot_id': line.lot_id.id,

                })
                dict.append(res.id)

        return [(6, 0, dict)]

    # here the action to get data from the wizard showed in list view and create stock picking
    def do_transfer_selected_lines(self):
        active_record_id = self._context.get('active_ids')[0]
        active_obj_location = self.env['stock.quant'].browse(active_record_id)

        for edata in self.stk_quant_ids:
            if edata.quantity_moved == 0 or edata.quantity_moved > edata.quantity:
                raise Warning("you can not make stock picking with this quantity !")
            if edata.location_id != active_obj_location.location_id:
                raise Warning("you can't make this action by selecting lines of different locations")
        operation=self.env['operation.operation'].search([('location_id','=',self.location_id.id)])
        vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': self.location_id.name,
            'operation_id': operation.id,

        }
        move_lines = []
        scan_product_ids_lst = []
        data_line = []
        u = 0

        for component in self.stk_quant_ids:
            line = [0, 0,
                    {'product_id': component.product_id.id, 'product_uom': component.product_id.uom_id.id,
                     'product_uom_qty': component.quantity_moved,
                     'name': component.product_id.name
                     }]

            if self.scan_option == 'withoutscan' and (component.product_id.tracking == 'lot' or component.product_id.tracking == 'serial'):
                scan_product_ids_lst.append([0, 0,
                    {
                    'product_id': component.product_id.id,
                    'product_uom_qty': component.quantity_moved,
                    'lot_no':component.lot_id.name,
                    }
                ])
                data_line.append(component.lot_id.id)

            if component.quantity != 0.0:
                move_lines.append(line)

        if len(move_lines) == 0:
            raise Warning(str("you can not make Stock Picking with no lines"))
        
        vals['move_lines'] = move_lines
        vals['scan_products_ids'] = scan_product_ids_lst
        

        res = self.env['stock.picking'].create(vals)
        res.action_confirm()
        # res.force_assign()
        # for l in res.move_lines:
        #     if l.product_id.tracking == 'lot' or l.product_id.tracking == 'serial':
        #         if l.product_id.id in data_line.keys():
        #             lot_id = data_line[l.product_id.id]
        #         else:
        #             lot_id = {'id' : False}
        #         vals = {
        #             'picking_id': res.id,
        #             'move_id': l.id,
        #             'qty_done': l.product_uom_qty,
        #             'lot_id': lot_id.id,
        #             'lot_name': lot_id.name,
        #             'location_id': l.location_id.id,
        #             'location_dest_id': l.location_dest_id.id,
        #             'product_id': l.product_id.id,
        #             'product_uom_id': 1,
        #             'product_uom_qty': 0,
        #         }
        #         self.env['stock.move.line'].create(vals)
        #
        #         u = u + 1
        #     l.write({'qty_done': l.product_uom_qty})

        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "form"]],
            "res_id": res.id,
            "target": "current",
        }

    # get default location
    @api.model
    def _get_location_name(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)[0]
        return active_obj.location_id

    # get default logged in user
    def _default_partner(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)
        location_id = active_obj.location_id
        # print (location_id.location_id.id)
        partner = self.env['res.partner'].search([('operations_location', '=', location_id.location_id.id)])[0]
        return partner

    # get picking type
    def _get_picking_type(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)
        warehouse_id = active_obj.location_id.warehouse_id
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse_id.id)])[0]
        return picking_type

    location_id = fields.Many2one('stock.location', string="Location", default=_get_location_name, readonly=True)
    location_dest_id = fields.Many2one(related="partner_id.property_stock_customer", store=True, readonly=True,
                                       string="Destination Location")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type", required=True,default=_get_picking_type)
    stk_quant_ids = fields.One2many('stock.quant.items', 'wizard_id', string="Stock Quant Items", required=False,
                                    default=get_stock_quant_lines)
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner", default=_default_partner)
    warehouse_id = fields.Many2one(related="location_id.warehouse_id",store=True,readonly=True,string="Warehouse")
    scan_option = fields.Selection([('withscan', 'With scan'), ('withoutscan', 'Without Scan')],string="Scan Option",default='withscan')


class stock_quant_details_items(models.TransientModel):
    _name = 'stock.quant.items'
    _description = 'Stock Quant Items'

    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Float(string="Qty")
    location_id = fields.Many2one('stock.location', string="Location")
    wizard_id = fields.Many2one('wizard_stock_quant', string="Wizard Name")
    wizard_id_back = fields.Many2one('wizard_back_to_warehouse', string="Wizard Name")
    wizard_id_move = fields.Many2one('wizard_move_to_location', string="Wizard Name")
    wizard_id_hanged = fields.Many2one('wizard_move_to_hanged_warehouse', string="Wizard Name")
    wizard_id_hanged_back = fields.Many2one('wizard_hanged_back_to_warehouse', string="Wizard Name")
    wizard_id_hanged_delivery = fields.Many2one('wizard_hanged_delivery', string="Wizard Name")
    quantity_moved = fields.Float(string="Quantity to be moved")
    lot_id = fields.Many2one('stock.production.lot', string="Lot", readonly=True)
    quant_id = fields.Many2one(comodel_name='hanged.stock.quant', string='Invoice', readonly=True)
