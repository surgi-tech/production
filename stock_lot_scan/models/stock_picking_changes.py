from datetime import datetime
import json
from pprint import pprint
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
import logging
from odoo import _

from odoo.exceptions import RedirectWarning
from odoo.exceptions import Warning
from odoo.exceptions import except_orm

import logging

_logger = logging.getLogger(__name__)


class stock_picking_inherit(models.Model):
    _name = 'temp.scan.product'

    product_id = fields.Many2one('product.product', string="Product", index=True)
    product_uom_qty = fields.Float(string="Qty")
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking")


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    ean13 = fields.Char(string="Scan", default='')
    ean132 = fields.Char(string="Scan")
    ean_out = fields.Char(string="Scan")
    supplier_ean13 = fields.Char(string="Supplier Scan")
    supplier_ean132 = fields.Char(string="Scan")
    scan_products_ids = fields.One2many('scan.product', 'stock_picking_id', string="Scanned Products")
    temp_products_ids = fields.One2many('temp.product', 'stock_picking_id', string="Temp. Products")
    temp_scan_products_ids = fields.One2many('temp.scan.product', 'stock_picking_id', string="Temp. Scan Products")
    pickin_Typ_code = fields.Selection(related='picking_type_id.code', string="Code")
    type_of_scaning = fields.Selection(
        [('first_group', 'First Group'), ('second_group', 'Second Group'), ('third_group', 'Third Group')],
        default='first_group')

    last_scanned_item = fields.Char("Last scanned", readonly=True)
    # operation_id = fields.Many2one("operation.operation", string="Operation ID")
    operation_id2 = fields.Many2one("operation.operation", string="Operation2 ID")

    # Ahmed Abd Al Aziz Code
    @api.onchange('ean13')  # when ean13 change
    def get_line_by_barcose(self):

        if self.ean13 != '':

            list = []
            serial = self.ean13
            lot_obj = self.env['stock.production.lot'].search([('name', '=', serial)])
            item_exist = False
            for rec in self:
                for scan in rec.scan_products_ids:
                    if scan.product_id.id == lot_obj.product_id.id:
                        scan.product_uom_qty = scan.product_uom_qty + 1
                        item_exist = True
                        pass  # end check product id exist

                    pass  # loop scan_product_ids
                if not item_exist:
                    list.append([0, 0, {
                        'product_id': lot_obj.product_id.id,
                        'lot_no': serial,
                        'product_uom_qty': 1,
                        'lot_name': lot_obj.lot_name,
                        'expiration_date': lot_obj.expiration_date,
                    }])
                    pass  # if the item not exist add it to list

                pass  # end check ean13 sent
            rec.scan_products_ids = list
            pass  # end for
            rec.ean13 = ''

        pass  # end function

    # synchronize Function
    def synchronize_scan(self):
        for rec in self:
            rec.do_unreserve()
            finalArray = {}
            for line in rec.scan_products_ids:
                if line.product_id.id in finalArray.keys():
                    finalArray[line.product_id.id].append({
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'lot_name': line.lot_name,
                        'lot_no': line.lot_no,
                    })
                else:
                    finalArray[line.product_id.id] = [{
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'lot_name': line.lot_name,
                        'lot_no': line.lot_no,
                    }]

            move_lines = rec.mapped('move_lines').filtered(lambda move: move.state not in ('cancel', 'done'))
            move_lines_product_ids = {}
            for line in move_lines:
                move_lines_product_ids[line.product_id.id] = {
                    'product_id': line.product_id.id,
                    'move_id': line.id,
                }

            for product_id, lots in finalArray.items():
                if product_id in move_lines_product_ids.keys():
                    move_id = move_lines_product_ids[product_id]['move_id']
                    line = rec.mapped('move_lines').filtered(lambda move: move.id == move_id)
                    move_line_ids = line.mapped('move_line_ids').filtered(
                        lambda move_line_id: move_line_id.state not in ('cancel', 'done'))
                    for lot in lots:
                        lot_id = rec.env['stock.production.lot'].search(
                            [('name', '=', lot['lot_no']), ('product_id', '=', product_id)])
                        if len(move_line_ids) > 0 and lot_id:
                            move_line_ids.write({
                                'qty_done': lot['product_uom_qty'],
                                'lot_id': lot_id.id,
                                'lot_name': lot_id.name,
                                # 'product_uom_qty': lot['product_uom_qty'],
                            })
                        elif lot_id:
                            vals = {
                                'qty_done': lot['product_uom_qty'],
                                'lot_id': lot_id.id,
                                'lot_name': lot_id.name,
                                'product_id': line.product_id.id,
                                # 'product_uom_qty': lot['product_uom_qty'],
                                'product_uom_id': line.product_uom.id,
                                'move_id': line.id,
                                'location_dest_id': rec.location_dest_id.id,
                                'location_id': rec.location_id.id,
                                'picking_id': rec.id,
                            }
                            self.env['stock.move.line'].sudo().create(vals)
                else:
                    for lot in lots:
                        lot_id = rec.env['stock.production.lot'].search(
                            [('name', '=', lot['lot_no']), ('product_id', '=', product_id)])
                        if lot_id:
                            product = self.env['product.product'].search([('id', '=', product_id)])
                            mov_id_var = {
                                'name': product.name,
                                'location_id': rec.location_id.id,
                                'picking_id': rec.id,
                                'location_dest_id': rec.location_dest_id.id,
                                'product_id': product_id,
                                'product_uom': product.uom_id.id,
                                'product_uom_qty': 0,
                                # 'ordered_qty': 0,
                            }
                            print("xxx")
                            move_id = rec.env['stock.move'].create({
                                'name': product.name,
                                'location_id': rec.location_id.id,
                                'picking_id': rec.id,
                                'location_dest_id': rec.location_dest_id.id,
                                'product_id': product_id,
                                'product_uom': product.uom_id.id,
                                'product_uom_qty': 0,
                                # 'ordered_qty': 0,
                            })
                            stock_move_var = {
                                'picking_id': rec.id,
                                'move_id': move_id.id,
                                'qty_done': lot['product_uom_qty'],
                                'lot_id': lot_id.id,
                                'lot_name': lot_id.name,
                                'location_dest_id': rec.location_dest_id.id,
                                'location_id': rec.location_id.id,
                                'product_id': product_id,
                                'product_uom_id': move_id.product_uom.id,
                                # 'product_uom_qty': 0,
                            }
                            print("vv")
                            rec.env['stock.move.line'].create({
                                'picking_id': rec.id,
                                'move_id': move_id.id,
                                'qty_done': lot['product_uom_qty'],
                                'lot_id': lot_id.id,
                                'lot_name': lot_id.name,
                                'location_dest_id': rec.location_dest_id.id,
                                'location_id': rec.location_id.id,
                                'product_id': product_id,
                                'product_uom_id': move_id.product_uom.id,
                                # 'product_uom_qty': 0,
                            })

            if rec.state == 'draft':
                print('+++++++++++++++++++++++++++++++++++++++++++++++++')
                rec.action_confirm()

            print('*********************************************************', move_lines)
            moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
            if not moves:
                raise UserError(_('Nothing to check the availability for.'))
            for move in moves:
                if move.product_tmpl_id.tracking == 'none':
                    move.quantity_done = move.product_uom_qty
                    v = move.quantity_done
                    z = move.product_uom_qty
                if move.state == 'assigned':
                    move.state = 'confirmed'
            moves._action_assign()
            return True

    @api.model
    def get_stock_lot_scan_data(self, active_id, cids=""):

        if active_id != "":
            rec = self.env['stock.picking'].search([('id', '=', active_id)])
            usecreatelotobj = rec.use_create_lots
            #  rec.company_id.id
            # companiesids=rec.env.company_ids
            # companiesids=allowed_companies = view_context.get('allowed_company_ids', False)
            if cids.find(',') != -1:
                componiesid = str(cids).split(",")
            else:
                componiesid = str(cids).split("%2C")
            print("f");
            # componiesid=[int(i) for i in componiesid]
            # componiesid=[1,2]
            lots = self.env['stock.production.lot'].search([('company_id', '=', rec.company_id.id)])

            quants = self.env['stock.quant'].search([('location_id', '=', rec.location_id.id)])

            data = {}
            quantsData = {}
            productsData = {}
            productsCodeData = {}
            linesData = {}
            datalower = {}
            for quant in quants:
                if quant.quantity > 0 and quant.reserved_quantity < quant.quantity:
                    lot = quant.lot_id
                    serial = lot.name
                    quant_quantity = quant.quantity - quant.reserved_quantity
                    if serial in quantsData and lot.product_id.id in quantsData[serial]:
                        quantsData[serial][lot.product_id.id] += quant_quantity
                    else:
                        quantsData[serial] = {}
                        quantsData[serial][lot.product_id.id] = quant_quantity
            rec = self.env['stock.picking'].search([('id', '=', active_id)])

            for lot in lots:
                serial = lot.name
                product_qty = 0
                if serial in quantsData and lot.product_id.id in quantsData[serial]:
                    product_qty = quantsData[serial][lot.product_id.id]
                if rec.picking_type_id.code == 'incoming':
                    product_qty = -1
                if serial in data:
                    if lot.expiration_date:
                        expdate = lot.expiration_date
                    else:
                        expdate = datetime.now() + timedelta(days=+300)
                    data[serial].append({
                        'product_id': lot.product_id.id,
                        'product_qty': product_qty,
                        'lot_no': serial,
                        'lot_name': lot.lot_name,
                        'expiration_date': str(expdate)
                    })
                    datalower[serial.lower()].append({
                        'product_id': lot.product_id.id,
                        'product_qty': product_qty,
                        'lot_no': serial,
                        'lot_name': lot.lot_name,
                        'expiration_date': str(expdate)
                    })
                else:
                    if "expiration_date" in lot:
                        expdate = lot.expiration_date
                    else:
                        expdate = datetime.now() + timedelta(days=+300)
                    data[serial] = [{
                        'product_id': lot.product_id.id,
                        'product_qty': product_qty,
                        'lot_no': serial,
                        # 'lot_name': lot.lot_name,
                        'expiration_date': str(expdate)
                    }]
                    datalower[serial.lower()] = [{
                        'product_id': lot.product_id.id,
                        'product_qty': product_qty,
                        'lot_no': serial,
                        # 'lot_name': lot.lot_name,
                        'expiration_date': str(expdate)
                    }]

            products = self.env['product.product'].search([])
            for product in products:
                product_id = product.id
                productsData[product_id] = {'id': product_id, 'name': product.name,
                                            'default_code': product.default_code, 'tracking': product.tracking}
                productsCodeData[product.default_code] = {'id': product_id, 'name': product.name,
                                                          'default_code': product.default_code,
                                                          'tracking': product.tracking}
            scan_lines = rec.scan_products_ids
            x = 0
            # productsCodeData={}
            for line in scan_lines:
                serial = line.lot_no
                if line.lot_no in data:
                    data[line.lot_no][0]['product_qty'] = line.product_availabilty
                if line.expiration_date:
                    expdate = line.expiration_date
                else:
                    expdate = None
                linesData[x] = {
                    'id': line.id,
                    'serial': serial,
                    'qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'lot_name': line.lot_name,
                    'expiration_date': str(expdate)
                }
                logging.warning("this is before function end >> " + str(line.expiration_date))
                x += 1
            returnData = {
                "data": data,
                "datalower": datalower,
                "products": productsData,
                'productsCodeData': productsCodeData,
                'res_id': active_id,
                'scan_lines': linesData,
                'type_of_scaning': rec.type_of_scaning,
                'pickin_Typ_code': rec.pickin_Typ_code,
                'usecreatelot': usecreatelotobj,
                'company_id':rec.company_id.id
            }
            print(returnData);
           # logging.warning(returnData)
            return json.dumps(returnData, ensure_ascii=False)

    def savebeforescanbutton(self):
        return True


class operation_stock_picking_inherit(models.Model):
    _inherit = 'operation.operation'

    stock_picking_operation = fields.One2many('stock.picking', 'operation_id', string="Inventory Transaction Operation",
                                              domain=[('pickin_Typ_code', '=', 'internal')])
    stock_picking_out = fields.One2many('stock.picking', 'operation_id', string="Inventory Transaction Out",
                                        domain=[('pickin_Typ_code', '=', 'outgoing')])
