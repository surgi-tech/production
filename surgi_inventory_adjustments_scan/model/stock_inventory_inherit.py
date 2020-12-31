import datetime
import json
# from xxlimited import Null

# from addons.stock.models import stock_inventory
from odoo import api, exceptions, fields, models
from odoo.exceptions import UserError, Warning, ValidationError


class stock_inventory_inherit(models.Model):
    _inherit = 'stock.inventory'
    # _name='stock.inventory'

    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[]")
    block = fields.Boolean(string="Block")
    scanning_box = fields.Char(string="Scan")
    scanning_mode = fields.Selection(
        [('internal_ref', 'By Internal reference'), ('lot_serial_no', 'By Lot/Serial Number')], string="Scanning Mode")

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(('You must define a warehouse for the company: %s.') % (company_user.name,))

    location_id = fields.Many2one(
        'stock.location', 'Inventoried Location',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        default=_default_location_id)

    @api.model
    def scan_from_ui(self, res_id, created, added):
        rec = self.search([('id', '=', res_id)])
        rec.line_ids.unlink()
        if len(created) > 0:
            for created_obj in created.values():
                for obj in created_obj.values():
                    print(str(obj))
                    self.env['stock.production.lot'].create(obj)

        if len(added) > 0:
            line_ids = []
            for scan_obj in added.values():
                for obj in scan_obj.values():
                    for key, value in obj.items():
                        if key == 'prod_lot_id_ref':
                            lot = self.env['stock.production.lot'].search(
                                [('name', '=', value), ('product_id', '=', obj['product_id'])])
                            if len(lot) > 0:
                                if len(lot) == 1:
                                    obj['prod_lot_id'] = lot.id
                                else:
                                    obj['prod_lot_id'] = lot[(len(lot) - 1)].id
                            del obj['prod_lot_id_ref']
                    line_ids.append([0, 0, obj])
            rec.line_ids = line_ids

    @api.model
    def get_stock_inventory_scan_data(self, active_id):
        if active_id is None or active_id is "Null":
            raise Warning(str("Please Save Your Product !!"))
        rec = self.env['stock.inventory'].search([('id', '=', active_id)])

        if rec.scanning_mode == False:
            raise Warning(str("You should select scanning mode first !!"))
        lots = self.env['stock.production.lot'].search([('company_id', '=', rec.company_id.id)])
        #lots = self.env['stock.production.lot'].search([])
        data = {}
        datalower={}
        productsData = {}
        productsCodeData = {}
        linesData = {}
        for lot in lots:
            serial = lot.name
            # lot_name = lot.lot_name
            lot_name = lot.name
            if rec.scanning_mode == 'lot_serial_no':
                ####### 2 check scanning box for $, to avoid redoing of 2,3,4,5 ########
                if '$' in serial:
                    lot_name = str(serial).split('$')[0]
                else:
                    lot_name = '-'
            serial = lot.name
            if serial in data:
                data[serial].append(
                    {'id': lot.id, 'product_id': lot.product_id.id, 'lot_no': serial, 'lot_name': lot_name,
                     # Ahmed Hashed 'expiration_date': str(lot.expiration_date)
                     })
                datalower[str(serial).lower()].append(
                    {'id': lot.id, 'product_id': lot.product_id.id, 'lot_no': serial, 'lot_name': lot_name,
                     # Ahmed Hashed 'expiration_date': str(lot.expiration_date)
                     })
            else:
                data[serial] = [{'id': lot.id, 'product_id': lot.product_id.id, 'lot_no': serial, 'lot_name': lot_name,
                                 # Ahmed Hashed 'expiration_date': str(lot.expiration_date)
                                 }]
                datalower[serial.lower()] = [{'id': lot.id, 'product_id': lot.product_id.id, 'lot_no': serial, 'lot_name': lot_name,
                                 # Ahmed Hashed 'expiration_date': str(lot.expiration_date)
                                 }]
        products = self.env['product.product'].search([])
        for product in products:
            product_id = product.id
            productsData[product_id] = {'id': product_id, 'name': product.name, 'default_code': product.default_code,
                                        'uom_id': product.uom_id.id, 'tracking': product.tracking}
            productsCodeData[product.default_code] = {'id': product_id, 'name': product.name,
                                                      'default_code': product.default_code, 'uom_id': product.uom_id.id,
                                                      'tracking': product.tracking}
        res = {'location_id': rec.location_id.id, 'location_name': rec.location_id.name,
               # Ahmed Hashed 'filter': rec.filter,
               # Ahmed Hashed 'exhausted': rec.exhausted,
               'date': str(rec.date), 'accounting_date': str(rec.accounting_date),
               'scanning_mode': rec.scanning_mode, 'state': rec.state, 'company_id': rec.company_id.id,
               'name': rec.name,
               # Ahmed Hashed 'package_id': rec.package_id.id,
               # AHmed Hashed 'partner_id': rec.partner_id.id
               }
        scan_lines = rec.line_ids
        x = 0
        for line in scan_lines:
            serial = line.prod_lot_id.name
            linesData[x] = {'id': line.id, 'serial': serial, 'cutSerial': serial, 'qty': line.scanned_quantity,
                            'product_id': line.product_id.id}
            x += 1
        # returnData = {"data": data, "products": productsData, 'productsCodeData': productsCodeData, 'res': res,
        # "res_id": active_id, 'scan_lines': linesData} #Ahmed Hashed
        returnData = {"data": data, "datalower": datalower,"products": productsData, 'productsCodeData' : { } , 'res': res,
                      "res_id": active_id, 'scan_lines': linesData}
        # returnData = {"data": data, "products": productsData, 'productsCodeData': productsCodeData, 'res': [],
        #               "res_id": active_id, 'scan_lines': linesData}
        print("xx")
        return json.dumps(returnData, ensure_ascii=False)

    # end of class
    pass


class stock_inventory_line_inherit(models.Model):
    _inherit = 'stock.inventory.line'

    location_id = fields.Many2one(
        'stock.location', 'Location', check_company=True,
        domain="[]",
        index=True, required=True)

    scanned_quantity = fields.Float(string="Scanned Quantity")

    # syncronize inventory lines
    def synchronize_inventorylines(self):
        filtered_lines = self.filtered(lambda l: l.state != 'done')
        for line in filtered_lines:
            #line.theoretical_qty=line.scanned_quantity
            line.product_qty = line.scanned_quantity
            #print(line.scanned_quantity)
            pass

        pass

    def action_reset_product_qty(self):
        """ Write `product_qty` to zero on the selected records. """
        res = super(stock_inventory_line_inherit, self).action_reset_product_qty()
        # raise  UserError("Entered")
        impacted_lines = self.env['stock.inventory.line']
        for line in self:
            if line.state == 'done':
                continue
            impacted_lines |= line
        impacted_lines.write({'product_qty': line.scanned_quantity})
        return res

    pass  # end class line inhert
