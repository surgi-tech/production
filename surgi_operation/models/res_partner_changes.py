from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models


class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    operations_location = fields.Many2one('stock.location', string="Operations Location")
    is_surgeon = fields.Boolean(string="Is a Surgeon")
    is_hospital = fields.Boolean(string="Is a Hospital")
    is_patient = fields.Boolean(string="Is a Patient")
    national_id = fields.Char('National ID')
    direct_sales_users = fields.Many2many('res.users',string="Direct Sales Users")

    gender = fields.Selection([('m', 'Male'), ('f', 'Female')])
    authority = fields.Selection([('closed', 'Closed'),('open', 'Open'),('open_approval', 'Open with Approval')], string='Authority Type')

    # hospital_stock_location_id = fields.Many2one('stock.location', string="Hospital Stock Location")
    customers_sales_order_location_id = fields.Many2one('stock.location', string="Customers Sales Order Location")


    def get_default_stock_config(self):
        customers_operations_location = self.env['ir.default'].get('stock.config.settings',
                                                                          'customers_operations_location')

        return customers_operations_location

    def get_default_stock_config2(self):
        customers_operations_location = self.env['ir.default'].get('stock.config.settings',
                                                                          'customers_operations_location')
        for rec in self:
            rec.customers_operations_location2 = customers_operations_location

    customers_operations_location = fields.Many2one('stock.location', string="Customers Operations Location",
                                                    default=get_default_stock_config
                                                    )

    customers_operations_location2 = fields.Many2one('stock.location', string="Customers Operations Location",
                                                     compute=get_default_stock_config2
                                                     )

    @api.model
    def create(self, vals):
        createdHospital = super(res_partner_inherit, self).create(vals)
        if 'customers_operations_location' in vals:
            customer_location = vals['customers_operations_location']

            values = {
                'name': vals['name'],
                'location_id':customer_location,
                'usage': "view",
                'partner_id': createdHospital.id,
            }
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            res = self.env['stock.location'].create(values)
            # ## Second location: internal location with hospital name + /stock as location name and created hospital as owner ##
            # secondLocationVals = {
            #     'name': 'Onshelf',
            #     'usage': "internal",
            #     'partner_id': createdHospital.id,
            #     'location_id': res.id
            # }
            # secondLocation = self.env['stock.location'].create(secondLocationVals)
            ## Second location: internal location with hospital name + /stock as location name and created hospital as owner ##
            secondLocationVals = {
                'name': 'Delivery',
                'usage': "customer",
                'partner_id': createdHospital.id,
                'delivery_order_location': True,
                'location_id': res.id
            }
            secondLocation = self.env['stock.location'].create(secondLocationVals)
            ## Third location: internal location with hospital name + /customers as location name and created hospital as owner ##
            thirdLocationVals = {
                'name': 'S-O',
                'usage': "customer",
                'partner_id': createdHospital.id,
                'sales_order_location': True,
                'location_id': res.id
            }
            thirdLocation = self.env['stock.location'].create(thirdLocationVals)
            createdHospital.write({
                                  'operations_location': res.id,
                                  #'hospital_stock_location_id': secondLocation.id,
                                  'property_stock_customer': secondLocation.id,
                                  'customers_sales_order_location_id': thirdLocation.id,
                                  })
        return createdHospital

    def unlink(self):
        for customer in self:
            stk_location = self.env['stock.location'].search(
                                                             [('name', '=', customer.name), ('location_id', '=', customer.customers_operations_location.id)])
            stk_location.unlink()
            return super(res_partner_inherit, self).unlink()

    def write(self, vals):
        customer_location_name = self.customers_operations_location2

        if not self.operations_location and False:
            values = {
                'name': self.name,
                'location_id': customer_location_name.id,
                'usage': "view",
            }
            res = self.env['stock.location'].create(values)
            vals['operations_location'] = res.id
            if 'active' in vals:
                res.write({'active': vals['active']})
            if 'name' in vals:
                res.write({'name': vals['name']})


        stk_location = self.env['stock.location'].search(
                                                         [('name', '=', self.name), ('location_id', '=', self.customers_operations_location.id)])
        if 'active' in vals:
            stk_location.write({'active': vals['active']})
        if 'name' in vals:
            stk_location.write({'name': vals['name']})
        return super(res_partner_inherit, self).write(vals)