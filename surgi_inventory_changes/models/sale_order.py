from odoo import models, fields, api,_

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_cocs= fields.Float(string="Total Cocs",)
    cocs_ids = fields.One2many(comodel_name="cocs.cocs", inverse_name="order_id",)

    total_sum_cocs= fields.Float(string="Total Cocs",)
    net_profit = fields.Float(string="Net Profit",  required=False, )
    # is_sum_cocs = fields.Boolean(string="",)

    # @api.depends('name')
    def compute_total_cocs(self):
        # for rec in self:
        total=0.0
        lines = [(5, 0, 0), ]
        lines22 = []

        for res in self.env['stock.picking'].search(['|',('sales_order_id.name','=',self.name),('group_id.name','=',self.name)]):
            total+=res.total_cocs

            if res.picking_type_id.code=='incoming':
                lines.append((0, 0, {
                    'picking_type_id':res.picking_type_id.id,
                    'total_cocs': -res.total_cocs,}))
                lines22.append(-res.total_cocs)
            else:
                lines22.append(res.total_cocs)

                lines.append((0, 0, {
                    'picking_type_id': res.picking_type_id.id,
                    'total_cocs': res.total_cocs,
                    'ref_stock':res.name,
                }))
        self.total_cocs=total
        # total2 = 0.0
        total2=sum(lines22)
        print(lines22,total2,'--------------------')
        self.net_profit=self.amount_total-total2
        self.update({'cocs_ids': lines,'total_sum_cocs':total2})





class NewModule(models.Model):
    _name = 'cocs.cocs'
    _rec_name = 'picking_type_id'

    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Picking Type", )
    total_cocs = fields.Float(string="Total Cocs", required=False, )
    ref_stock = fields.Char(string="Reference", required=False, )
    order_id = fields.Many2one(comodel_name="sale.order", string="", required=False, )

