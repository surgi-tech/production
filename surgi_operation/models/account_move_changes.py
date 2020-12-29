# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    # def _get_has_operation(self):
    #     for rec in self:
    #         rec.has_operation =  len(rec.operation_ids) > 0

    operation_ids = fields.One2many('operation.operation', 'invoice_id', 'Related Operation')
    ## Get From Operantions
    operation_id = fields.Many2one('operation.operation','Related Operation')
    patient_name = fields.Char(string="Patient Name")
    surgeon_id = fields.Many2one('res.partner', string="Surgeon", track_visibility='onchange')
    # ============= NewFields ================
    # Additional Fiels for the new cycle (Operation type) By SURGI-TECH
    hospital_id = fields.Many2one('res.partner', string="Hospital", track_visibility='onchange')
    customer_printed_name = fields.Char(string="Customer Printed Name")
    sales_area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", related='team_id.user_id',
                                         readonly=True)
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')
    # collection_team = fields.Many2one('crm.team', 'Collection Team', readonly=True, default=lambda self: self.env['crm.team'].search(['|', ('user_id', '=', self.collection_rep.id), ('member_ids', '=', self.collection_rep.id)],limit=1) ,track_visibility='onchange')

    has_operation = fields.Boolean("Has Operation")#, compute='_get_has_operation'
    quant_ids = fields.One2many('hanged.stock.quant', 'invoice_id', 'Related Quant')
    invoice_printing_description = fields.Text('Invoice Printing Description')
    print_description = fields.Boolean('Print Description', default=False)
    exchange_invoices = fields.Boolean("Exchanged invoices")
    exchange_invoices_id = fields.Many2one('account.move', 'Exchange invoices No.')

    @api.model
    def create(self, vals):
        res = super(AccountInvoiceInherit, self).create(vals)
        if res.has_operation:
            for operation_id in res.operation_ids:
                operation_type = operation_id.operation_type
                res.invoice_printing_description = operation_type.invoice_printing_description

        return res
