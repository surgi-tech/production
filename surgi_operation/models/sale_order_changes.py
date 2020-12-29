from odoo import api
from odoo import fields
from odoo import models

class sale_order(models.Model):
    _inherit = "sale.order"

    location_id = fields.Many2one(comodel_name='stock.location', string='Location')
    location_dest_id = fields.Many2one(comodel_name='stock.location', string="Destination Location")
    operation_id = fields.Many2one(comodel_name='operation.operation', string="Related Operation")
    # ============= NewFields ================
    # Additional Fiels for the new cycle (Operation type) By SURGI-TECH
    hospital_id = fields.Many2one('res.partner', string="Hospital", track_visibility='onchange')
    surgeon_id = fields.Many2one('res.partner', string="Surgeon", track_visibility='onchange')
    patient_name = fields.Char(string="Patient Name")
    customer_printed_name = fields.Char(string="Customer Printed Name")
    sales_area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", related='team_id.user_id',readonly=True)
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')
    #collection_team = fields.Many2one('crm.team', 'Collection Team', readonly=True, default=lambda self: self.env['crm.team'].search(['|', ('user_id', '=', self.collection_rep.id), ('member_ids', '=', self.collection_rep.id)],limit=1) ,track_visibility='onchange')

    # ============= NewFields ================
    # for the new cycle (Operation type) By Zienab Moesy

    so_type = fields.Selection([('normal', 'Normal'),
                                ('operation', 'Operation'),
                                ('tender', 'Tender'),
                                ('supply_order', 'Supply Order'),
                                ], string='Sale Order Type', default="normal")
    message_error = fields.Char(readonly=True)
    flag = fields.Boolean()
    oper_count = fields.Char("Operation Location Quant", compute='get_operation_count')

    def get_operation_count(self):
        for rec in self:
            if rec.so_type == 'tender' or rec.so_type == 'supply_order':
                operations = self.env['operation.operation'].search(['|','|',('tender_so', '=', rec.id),('supply_so', '=', rec.id),('state','=','confirm')])
                if operations:
                    print ('operation',operations)
                    rec.oper_count = len(operations)
                else:
                    rec.oper_count ='0'
            else:
                rec.oper_count='0'


    def action_view_operations(self):
        for rec in self:
            compose_tree = self.env.ref('operation.operation', False)
            operations = self.env['operation.operation'].search(['|',('tender_so', '=', rec.id),('supply_so', '=', rec.id),('state','=','confirm')])
            list = []
            for op in operations:
                list.append(op.id)
            return {
                'name': "Operations",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'field_parent': 'child_ids',
                'res_model': 'operation.operation',
                'target': 'current',
                'domain': [('id', 'in', list)],
                # 'context': {"search_default_type_group":1,},
            }


    def action_confirm(self):
        res = super(sale_order, self).action_confirm()
        pickings = self.mapped('picking_ids')
        if self.location_id and self.location_id.id:
            for picking in pickings:
                picking.write({
                    'location_id': self.location_id.id,
                    'operation_id': self.operation_id.id if self.operation_id else False,
                })
        if self.location_dest_id and self.location_dest_id.id:
            for picking in pickings:
                picking.write({
                    'location_dest_id': self.location_dest_id.id,
                    'operation_id': self.operation_id.id if self.operation_id else False,
                })
        return res

    def action_invoice_create(self, grouped=False, final=False):
        res = super(sale_order, self).action_invoice_create(grouped, final)
        if self.operation_id:
            for invoice_id in res:
                self.operation_id.invoice_id = invoice_id
        return res


    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id.is_hospital:
    #         self.so_type = "tender"
    #         self.flag = True
    #         partner_location = self.env['stock.location'].search(
    #             [('partner_id', '=', self.partner_id.id), ('usage', '=', 'customer')])
    #         self.location_dest_id = partner_location.id
    #     else:
    #         self.so_type = ''
    #         self.flag = True
    #
    # @api.onchange('so_type')
    # def _onchange_so_type(self):
    #     if self.so_type == 'tender':
    #         if self.partner_id.is_hospital:
    #             self.flag = True
    #             self.message_error = ''
    #             partner_location = self.env['stock.location'].search(
    #                 [('partner_id', '=', self.partner_id.id), ('usage', '=', 'customer')])
    #             # self.location_dest_id = partner_location.id
    #             self.location_dest_id = self.partner_id.customers_sales_order_location_id
    #         else:
    #             self.message_error = "Customer must be hospital first"
    #             self.so_type = ''
    #             self.flag = False
    #     else:
    #         self.flag = True
    #         self.message_error = ''

    @api.onchange('so_type')
    def _onchange_so_type(self):
        if self.so_type == 'supply_order':
            self.location_dest_id = self.partner_id.customers_sales_order_location_id
        elif self.so_type == 'operation':
            self.location_dest_id = self.partner_id.property_stock_customer
        else:
            self.location_dest_id = ""