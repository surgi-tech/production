from odoo import models, fields, api,_
from datetime import datetime,date

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'


    sale_create_date = fields.Date(string="Create Date",tracking=True,)
    stock_control_cycle_start = fields.Date(string="Stock Control Cycle Start",tracking=True,)
    stock_control_cycle_end = fields.Date(string="Stock Control Cycle End",tracking=True,)
    confirmation_date = fields.Date(string="Confirmation Date",tracking=True)
    delivery_done_date = fields.Date(string="Delivery Done Date",tracking=True)
    invoiced_date = fields.Date(string="Invoiced Date",tracking=True)

    is_scss = fields.Boolean(string="",  )
    is_scse = fields.Boolean(string="",  )

    @api.model
    def create(self, values):
        res=super(SaleOrderInherit, self).create(values)
        res.sale_create_date=date.today()
        return res

    def button_sccs(self):
        self.stock_control_cycle_start=date.today()
        self.is_scss=True

    def button_scce(self):
        self.stock_control_cycle_end=date.today()
        self.is_scse=True

    def action_confirm(self):
        res=super(SaleOrderInherit, self).action_confirm()
        self.confirmation_date=date.today()
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_delivery_date = fields.Boolean(string="",compute='compute_is_delivery_date')

    @api.depends('state','sale_id')
    def compute_is_delivery_date(self):
        self.is_delivery_date=False
        for rec in self:
            if rec.date_done:
                date_done = datetime.strptime(str(rec.date_done).split(".")[0], '%Y-%m-%d %H:%M:%S').date()

                if rec.state=='done' and rec.sale_id:
                    rec.sale_id.delivery_done_date=date_done


class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res=super(SaleAdvancePaymentInvInherit, self).create_invoices()
        sales_record = self.env['sale.order'].browse(self._context.get('active_ids'))
        if sales_record:
            for sale in sales_record:
                sale.invoiced_date=date.today()

        return res
