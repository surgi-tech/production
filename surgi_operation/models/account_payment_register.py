
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class payment_register_surgi(models.TransientModel):
    _inherit = 'account.payment.register'

    check_number = fields.Char(string="Check Number", readonly=False, copy=False, default=0,
                               help="Number of the check corresponding to this payment. If your pre-printed check are not already numbered, "
                                    "you can manage the numbering in the journal configuration page.")

    date_due = fields.Date('Due Date', readonly=False)
    collection_receipt_number = fields.Integer(string="Receipt Number")
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')
    collection_rep_name = fields.Char(string="Collection Rep", track_visibility='onchange')
    second_approval = fields.Boolean("Second Approval")
