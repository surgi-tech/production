from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models


class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    def _default_uom(self):
        uom_categ_id = self.env.ref('uom.product_uom_unit').id
        return self.env['uom.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)

    def open_stock_wizard_cancel_operation(self):
        action = self.env.ref('surgi_operation.action_cancel_stock_wizard_view')
        result = action.read()[0]
        res = self.env.ref('surgi_operation.action_cancel_stock_wizard_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result

    reason = fields.Many2one(comodel_name='operation.cancel.reason', string="Reason")
    description = fields.Text(string="Description")
    weight_uom_id = fields.Many2one('uom.uom', default=_default_uom)
    surgeries_supply_checked = fields.Boolean(related="picking_type_id.surgeries_supply",
                                              string="Surgeries Supply type")
    operation_components_ids = fields.Many2many('product.product', string="Components", readonly=True)
    operation_product_lines = fields.One2many('product.operation.line', 'picking_id', string="products", readonly=True)
    operation_id = fields.Many2one("operation.operation", string="Operation ID")

    # ========== Z.morsy ==============
    # Adding is delivered check box
    reviewed = fields.Boolean(string='Reviewed')

    # Adding operation id field
    # operation_id=fields.Many2one('operation.operation', string='Operation')

    # Adding function set Reviewed
    def setReviewed(self):
        self.write({'reviewed': True})

    @api.model
    def create(self, vals):
        loc_des_id = vals['location_dest_id']
        partner = vals['partner_id']
        partner_obj = self.env['res.partner'].browse(partner)
        partner_obj_op_loc = partner_obj.operations_location.id
        picking_type = vals['picking_type_id']
        # raise Warning (str(picking_type.warehouse_id.id))
        pick_typpe = self.env['stock.picking.type'].browse(picking_type)
        # raise Warning (str(pick_typpe.warehouse_id.id))
        if "operation_id" in vals:
            vals['operation_components_ids'] = [(4, operation.id) for operation in
                                                self.env['operation.operation'].browse(
                                                    vals['operation_id']).component_ids]

            prod_lines = []
            for ln in self.env['operation.operation'].browse(vals['operation_id']).product_lines:
                line = [0, False, {
                    'product_id': ln.product_id.id,
                    'quantity': ln.quantity,
                    'operation_id': self.operation_id.id, }]
                prod_lines.append(line)
            vals['operation_product_lines'] = prod_lines
        if not loc_des_id:
            values = {
                'name': "fake name to be updated from ress.name ",
                'usage': "transit",
                'location_id': partner_obj_op_loc,
                'is_operation_location': True,
                'warehouse_id': pick_typpe.warehouse_id.id
            }
            res = self.env['stock.location'].create(values)
            vals['location_dest_id'] = res.id

            ress = super(stock_picking_inherit, self).create(vals)
            res.write({'name': ress.name})
            # raise Warning(str(ress))
            return ress
        else:
            return super(stock_picking_inherit, self).create(vals)

    # here to change the default of loading default values of location_destination_id
    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                if self.surgeries_supply_checked == False:
                    location_dest_id = self.picking_type_id.default_location_dest_id.id
                else:
                    location_dest_id = False
            elif self.partner_id:
                if self.surgeries_supply_checked == False:
                    location_dest_id = self.partner_id.property_stock_customer.id
                else:
                    location_dest_id = False
            else:
                if self.surgeries_supply_checked == False:
                    location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()
                else:
                    supplierloc = self.env['stock.warehouse']._get_partner_locations()
                    location_dest_id = False

            self.location_id = location_id
            self.location_dest_id = location_dest_id
        # TDE CLEANME move into onchange_partner_id
        if self.partner_id:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in (
                    'no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}

    def button_validate1(self):
        for rec in self:
            # raise Warning(rec.move_line_ids_without_package)
            dist_warehouse = self.env['stock.warehouse'].search([('is_hanged_warehouse', '=', True)])
            location = self.env['stock.location'].search(
                [('warehouse_id', '=', dist_warehouse.id), ('is_operation_location', '=', True),
                 ('usage', '=', 'internal')])
            # raise Warning(rec.location_dest_id.id)
            if rec.location_id.id == location.id:
                for line in rec.move_lines:
                    quant_line_delete = self.env['hanged.stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),
                         ('quantity', '=', line.quantity_done), ])
                    quant_line_delete.unlink()
                    quant_line_update = self.env['hanged.stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)])
                    quant_line_update.write({
                        'quantity': quant_line_update.quantity - line.quantity_done
                    })
            elif rec.location_dest_id.id == location.id:
                print("ff")
                op = rec.operation_id.id
                for line in rec.move_lines:
                    ##raise Warning(line.name)
                    # lot=self.env['stock.production.lot'].search(['company_id','=',line.company_id.id,('product_id', '=', line.product_id.id),('name','=',line.lot_name)])
                    # raise Warning(lot.id)
                    # quant_line = self.env['stock.quant'].search([('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),('lot_id','=',line.move_line_ids.lot_id.id)])
                    quant_line = self.env['stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),
                         ('lot_id', '=', line.move_line_ids.lot_id.id)])
                    # raise Exception(quant_line)
                    if quant_line:
                        self.env['hanged.stock.quant'].create({
                            'quant_id': quant_line.id,
                            'product_id': quant_line.product_id.id,
                            'location_id': location.id,
                            'operation_location_id': quant_line.location_id.id,
                            'is_wh_user': quant_line.is_wh_user,
                            'is_operation_related': quant_line.is_operation_related,
                            'reserved_quantity': quant_line.reserved_quantity,
                            'quantity': line.quantity_done,
                            'lot_id': quant_line.lot_id.id,
                            'package_id': quant_line.package_id.id,
                            'owner_id': quant_line.owner_id.id,
                            'product_uom_id': quant_line.product_uom_id.id,
                            'company_id': quant_line.company_id.id,
                            'operation_id': op
                        })
        return super(stock_picking_inherit, self).button_validate()

    def button_validate(self):
        for rec in self:
            # raise Warning(rec.move_line_ids_without_package)
            dist_warehouse = self.env['stock.warehouse'].search([('is_hanged_warehouse', '=', True)])
            location = self.env['stock.location'].search(
                [('warehouse_id', '=', dist_warehouse.id), ('is_operation_location', '=', True),
                 ('usage', '=', 'internal')])
            # raise Warning(rec.location_dest_id.id)
            if rec.location_id.id == location.id:
                for line in rec.move_lines:
                    quant_line_delete = self.env['hanged.stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),
                         ('quantity', '=', line.quantity_done), ])
                    quant_line_delete.unlink()
                    quant_line_update = self.env['hanged.stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)])
                    quant_line_update.write({
                        'quantity': quant_line_update.quantity - line.quantity_done
                    })
            elif rec.location_dest_id.id == location.id:
                print("ff")
                op = rec.operation_id.id
                for line in rec.move_line_ids_without_package:
                    ##raise Warning(line.name)
                    # lot=self.env['stock.production.lot'].search(['company_id','=',line.company_id.id,('product_id', '=', line.product_id.id),('name','=',line.lot_name)])
                    # raise Warning(lot.id)
                    # quant_line = self.env['stock.quant'].search([('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),('lot_id','=',line.move_line_ids.lot_id.id)])
                    quant_line = self.env['stock.quant'].search(
                        [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id),
                         ('lot_id', '=', line.lot_id.id)])
                    # raise Exception(quant_line)
                    if quant_line:
                        self.env['hanged.stock.quant'].create({
                            'quant_id': quant_line.id,
                            'product_id': quant_line.product_id.id,
                            'location_id': location.id,
                            'operation_location_id': quant_line.location_id.id,
                            'is_wh_user': quant_line.is_wh_user,
                            'is_operation_related': quant_line.is_operation_related,
                            'reserved_quantity': quant_line.reserved_quantity,
                            'quantity': line.qty_done,
                            'lot_id': quant_line.lot_id.id,
                            'package_id': quant_line.package_id.id,
                            'owner_id': quant_line.owner_id.id,
                            'product_uom_id': quant_line.product_uom_id.id,
                            'company_id': quant_line.company_id.id,
                            'operation_id': op
                        })
        return super(stock_picking_inherit, self).button_validate()

