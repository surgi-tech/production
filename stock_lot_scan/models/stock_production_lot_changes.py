from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models


class stock_production_lot_inherit(models.Model):
    _inherit = 'stock.production.lot'

    @api.onchange('expiration_date')
    def get_exp_date(self):
        date = self.expiration_date
        #current_date=fields.Datetime.now().date()
        #self.lot.expiration_date=self.expiration_date.date()
        #self.lot.expiration_date=self.expiration_date
        #self.life_date = date

    @api.depends('expiration_date')
    def _compute_product_expiry_alert(self):
        current_date = fields.Datetime.now().date()
        for lot in self:
            if lot.expiration_date:
                lot.product_expiry_alert = lot.expiration_date <= current_date
            else:
                lot.product_expiry_alert = False

