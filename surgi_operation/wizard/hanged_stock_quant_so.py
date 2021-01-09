from odoo import fields, models, api, exceptions
from odoo.exceptions import UserError, Warning


class hanged_stock_quant_so(models.TransientModel):
    _name = "hanged.stock.quant.so"

    @api.model
    def get_stock_quant_lines(self):
        stock_active_ids = self._context.get('active_ids')
        stock_ids = self.env['hanged.stock.quant'].browse(stock_active_ids)

        dict = []
        for stk in stock_ids:
            for line in stk:
                res = self.env['stock.quant.items.so'].create({
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'quant_id':line.id,
                    'location_id':line.location_id.id,
                })
                dict.append(res.id)

        return [(6, 0, dict)]

    def do_transfer_selected_lines(self):
        active_record_id = self._context.get('active_ids')[0]
        active_record_ids = self._context.get('active_ids')
        active_obj_location = self.env['hanged.stock.quant'].browse(active_record_id)
        active_obj_locations = self.env['hanged.stock.quant'].browse(active_record_ids)
        operation_location_id = active_obj_location.operation_location_id
        for active_obj_location in active_obj_locations:
            if active_obj_location.operation_location_id != operation_location_id:
                raise Warning("you can't make this action by selecting lines of different locations")

        operation_id = False
        for edata in self.stk_quant_ids:
            if edata.quantity == 0:
                raise Warning("you can not create invoice with this quantity !")
            if edata.quant_id and edata.quant_id.invoice_id:
                raise Warning('You can not make invoice on invoiced lines!')
            operation_id = self.env['operation.operation'].search([('name','=',edata.quant_id.operation_location_id.name)])

        vals = {
            'type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'account_id': self.partner_id.property_account_receivable_id.id,
        }
        if operation_id:
            vals['operation_ids'] = [(6, 0, [operation_id.id])]
            vals['operation_id'] = operation_id.id
            vals['operation_id'] = operation_id.patient_name
            vals['operation_id'] = operation_id.surgeon_id and operation_id.surgeon_id.id
        if self.partner_id.property_product_pricelist:
            vals['currency_id'] = self.partner_id.property_product_pricelist.currency_id.id
        if self.partner_id.property_payment_term_id:
            vals['payment_term_id'] = self.partner_id.property_payment_term_id.id
        dict = []
        for component in self.stk_quant_ids:
            dict.append(component.quant_id.id)

        vals['quant_ids'] = [(6, 0, dict)]
        res = self.env['account.move'].create(vals)

        for component in self.stk_quant_ids:
            price = 0
            account_id = component.product_id.property_account_income_id.id
            if not account_id:
                account_id = component.product_id.categ_id.property_account_income_categ_id.id
            for item in self.partner_id.property_product_pricelist.item_ids:
                if component.product_id.id == item.product_id.id:
                    price = item.fixed_price
            self.env['account.move.line'].create({
                'payment_term_id': res.payment_term_id.id if res.payment_term_id else None,
                'product_id': component.product_id.id,
                'name': 'Hanged Quantities Invoice',
                'account_id': account_id,
                'quantity': component.quantity,
                'uom_id': component.product_id.uom_id.id,
                'price_unit': price,
                'invoice_id': res.id,
            })

        form_id = self.env.ref('account.view_move_form', False)

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            'views': [(form_id.id, 'form')],
            "res_id": res.id,
            "target": "current",
        }

    def _default_partner(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['hanged.stock.quant'].browse(active_record)
        location_id = active_obj.operation_location_id
        # print (location_id.location_id.id)
        partner = self.env['res.partner'].search([('operations_location', '=', location_id.location_id.id)])[0]
        return partner

    @api.model
    def _get_location_name(self):
        active_record = self._context.get('active_ids')[0]
        active_obj = self.env['hanged.stock.quant'].browse(active_record)[0]
        return active_obj.location_id

    stk_quant_ids = fields.One2many('stock.quant.items.so', 'wizard_id_hanged_so', string="Stock Quant Items", required=False, default=get_stock_quant_lines)
    partner_id = fields.Many2one('res.partner', string="Partner", default=_default_partner)
    location_id = fields.Many2one('stock.location', string="Location", default=_get_location_name, readonly=True)

class stock_quant_details_items(models.TransientModel):
    _name = 'stock.quant.items.so'
    _description = 'Stock Quant Items SO'

    product_id = fields.Many2one('product.product', string="Product")
    quant_id = fields.Many2one('hanged.stock.quant', string="Quant")
    quantity = fields.Float(string="Qty")
    location_id = fields.Many2one('stock.location', string="Location", readonly=True)
    wizard_id_hanged_so = fields.Many2one('hanged.stock.quant.so', string="Wizard Name")