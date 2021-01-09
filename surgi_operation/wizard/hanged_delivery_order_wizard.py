from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError, Warning


class wizard_stock_quant(models.TransientModel):
    _name = "wizard_hanged_delivery"

    # here we get data from selected lines and show it into wizard
    @api.model
    def get_stock_quant_lines(self):
        stock_active_ids = self._context.get('active_ids')
        stock_ids = self.env['hanged.stock.quant'].browse(stock_active_ids)

        dict = []
        for stk in stock_ids:
            for line in stk:
                res = self.env['stock.quant.items'].create({
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'quantity_moved': line.quantity,
                    'location_id': line.location_id.id,
                    'lot_id': line.lot_id.id,
                    'quant_id': line.id,

                })
                dict.append(res.id)

        return [(6, 0, dict)]

    # here the action to get data from the wizard showed in list view and create stock picking
    def do_transfer_selected_lines(self):
        active_record_id = self._context.get('active_ids')[0]
        active_record_ids = self._context.get('active_ids')
        active_obj_location = self.env['hanged.stock.quant'].browse(active_record_id)
        active_obj_locations = self.env['hanged.stock.quant'].browse(active_record_ids)
        operation_location_id = active_obj_location.operation_location_id
        for active_obj_location in active_obj_locations:
            if active_obj_location.operation_location_id != operation_location_id:
                raise Warning("you can't make this action by selecting lines of different locations")



        for edata in self.stk_quant_ids:
            if edata.quantity_moved == 0 or edata.quantity_moved > edata.quantity:
                raise Warning("you can not make stock picking with this quantity !")
            if edata.quant_id and not edata.quant_id.invoice_id:
                raise Warning('You can not make stock picking with un-invoiced lines!')
        vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': self.location_id.name,

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
        active_obj = self.env['hanged.stock.quant'].browse(active_record)[0]
        # dist_warehouse = self.env['stock.warehouse'].search([('is_hanged_warehouse', '=', True)])
        # location = self.env['stock.location'].search(
        #     [('warehouse_id', '=', dist_warehouse.id), ('is_operation_location', '=', True),
        #      ('usage', '=', 'internal')])
        return active_obj.location_id

    # get default logged in user
    def _default_partner(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['hanged.stock.quant'].browse(active_record)
        location_id = active_obj.operation_location_id
        # print (location_id.location_id.id)
        partner = self.env['res.partner'].search([('operations_location', '=', location_id.location_id.id)])[0]
        return partner

    # get picking type
    def _get_picking_type(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['hanged.stock.quant'].browse(active_record)
        warehouse_id = active_obj.location_id.warehouse_id
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', warehouse_id.id)])[0]
        return picking_type

    location_id = fields.Many2one('stock.location', string="Location", default=_get_location_name, readonly=True)
    location_dest_id = fields.Many2one(related="partner_id.property_stock_customer", store=True, readonly=True,
                                       string="Destination Location")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type", required=True,default=_get_picking_type)
    stk_quant_ids = fields.One2many('stock.quant.items', 'wizard_id_hanged_delivery', string="Stock Quant Items", required=False,
                                    default=get_stock_quant_lines)
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner", default=_default_partner)
    warehouse_id = fields.Many2one(related="location_id.warehouse_id",store=True,readonly=True,string="Warehouse")
    scan_option = fields.Selection([('withscan', 'With scan'), ('withoutscan', 'Without Scan')],string="Scan Option",default='withscan')