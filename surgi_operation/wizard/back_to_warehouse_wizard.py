from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
from odoo.exceptions import Warning


class wizard_back_to_warehouse(models.TransientModel):
    _name = "wizard_back_to_warehouse"

    # here we get data from selected lines and show it into wizard
    @api.model
    def get_stock_back_to_warehouse_lines(self):
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

        return [(6,0,dict)]

    # here the action to get data from the wizard showed in list view and create stock picking
    def do_transfer_selected_lines(self):
        active_record_id = self._context.get('active_ids')[0]
        active_obj_location = self.env['stock.quant'].browse(active_record_id)

        for edata in self.stk_quant_ids:
            if edata.quantity_moved == 0 or edata.quantity_moved > edata.quantity:
                raise Warning("you can not make stock picking with this quantity !")
            if edata.location_id != active_obj_location.location_id:
                raise Warning("you can't make this action by selecting lines of different locations")

        self.seq_no = self.env['ir.sequence'].get('back_to_warehouse_number')
        operation=self.env['operation.operation'].search([('location_id','=',self.location_id.id)])

        vals = {
            'name':self.location_id.name + self.seq_no,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': self.location_id.name,
            'operation_id': operation.id,
        }
        move_lines = []
        scan_product_ids_lst = []
        temp_scan_products_ids_lst = []
        data_line = []
        for component in self.stk_quant_ids:
            if component.quantity != 0.0:
                line = [0, 0,
                    {'product_id': component.product_id.id, 'product_uom': component.product_id.uom_id.id,
                        'product_uom_qty': component.quantity_moved,
                        'name': component.product_id.name
                        }]
                move_lines.append(line)

                if component.product_id.tracking == 'lot' or component.product_id.tracking == 'serial':
                    line2 = [0, 0,
                        {'product_id': component.product_id.id,
                            'product_uom_qty': component.quantity_moved,
                            'lot_no': component.lot_id.name,
                            }]
                    scan_product_ids_lst.append(line2)
                    temp_scan_products_ids_lst.append([0, 0, {'product_id':component.product_id.id, 'product_uom_qty':component.quantity_moved}])


        vals['move_lines'] = move_lines
        if self.scan_option == 'withoutscan':
            vals['scan_products_ids'] = scan_product_ids_lst
            vals['temp_scan_products_ids'] = temp_scan_products_ids_lst

        if len(move_lines) == 0:
            raise Warning(str("you can not make Stock Picking with no lines"))

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
        active_obj = self.env['stock.quant'].browse(active_record)
        return active_obj.location_id

    # get default logged in user
    def _default_partner(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)
        location_id = active_obj.location_id
        partner = self.env['res.partner'].search([('operations_location', '=', location_id.location_id.id)], limit=1)
        print(location_id.location_id)
        print(partner)
        return partner


    # get picking type
    def _get_picking_type(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)
        warehouse_id = active_obj.location_id.warehouse_id
        # print "picking "+str(warehouse_id.name)
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id', '=', warehouse_id.id), ('surgeries_supply', '=', True)])
        return picking_type

    # get_location_dest_id
    def _get_location_dest_id(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['stock.quant'].browse(active_record)
        parent_location = active_obj.location_id.warehouse_id
        location_dest_id = self.env['stock.location'].search(
                                                             [('location_id.name', '=', parent_location.name), ('usage', '=', 'internal')])
        return location_dest_id



    location_id = fields.Many2one('stock.location', string="Location", default=_get_location_name, readonly=True)
    location_dest_id = fields.Many2one('stock.location', string="Destination Location", required=True, default=_get_location_dest_id,)
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type", required=True, default=_get_picking_type,)
    stk_quant_ids = fields.One2many('stock.quant.items', 'wizard_id_back', string="Stock Quant Items", required=False,
                                    default=get_stock_back_to_warehouse_lines)
    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner", default=_default_partner)
    warehouse_id = fields.Many2one(related="location_id.warehouse_id", store=True, readonly=True, string="Warehouse")
    seq_no = fields.Char(string="Request Reference", required=True, readonly=True, select=True,
                         copy=False, default='New')
    scan_option = fields.Selection([('withscan', 'With scan'), ('withoutscan', 'Without Scan')], required=True)

