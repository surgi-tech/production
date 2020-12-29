from odoo import fields, models, api, exceptions


class stock_config_settings_inherit(models.TransientModel):
    _inherit = 'res.config.settings'

    customers_operations_location = fields.Many2one('stock.location', string="Customers Operations Location")

    @api.model
    def get_default_stock_config(self,fields):
        customers_operations_location = self.env['ir.default'].get('res.config.settings','customers_operations_location')
        return {
            'customers_operations_location': customers_operations_location,}

    @api.model
    def set_stock_defaults(self):
        self.ensure_one()

        self.env['ir.default'].sudo().set('res.config.settings', 'customers_operations_location', self.customers_operations_location.id,)
