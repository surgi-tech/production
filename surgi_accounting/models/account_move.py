# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
# from json import dumps
#
# import json
# import re

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    customer_printed_name = fields.Char(string="Customer Printed Name")
    sales_area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", readonly=True)#related='team_id.user_id',
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')

    invoice_printing_description = fields.Text('Invoice Printing Description')
    print_description = fields.Boolean('Print Description', default=False)
    exchange_invoices = fields.Boolean("Exchanged invoices")
    exchange_invoices_id = fields.Many2one('account.move', 'Exchange invoices No.')

    date_reconcile = fields.Date(string="Date", )#compute='_compute_payments_widget_reconciled_info'
    payment_name = fields.Char(string="Payment Name",)#compute='_compute_payments_widget_reconciled_info'

    # @api.depends('type', 'line_ids.amount_residual')
    # def _compute_payments_widget_reconciled_info(self):
    #     self.date_reconcile=False
    #     self.payment_name=""
    #     for move in self:
    #         if move.state != 'posted' or not move.is_invoice(include_receipts=True):
    #             move.invoice_payments_widget = json.dumps(False)
    #             continue
    #         reconciled_vals = move._get_reconciled_info_JSON_values()
    #         print("111111111111",reconciled_vals)
    #         for recs in reconciled_vals:
    #             move.date_reconcile = recs['date']
    #
    #         for pay in self.env['account.payment'].search([]):
    #             if move.id in pay.invoice_ids.ids:
    #                 print("1111111111111ffffffffffffffffffffffffffffffffffffffffffffffff",pay.name)
    #                 move.payment_name = pay.name
    #
    #         if reconciled_vals:
    #             info = {
    #                 'title': _('Less Payment'),
    #                 'outstanding': False,
    #                 'content': reconciled_vals,
    #             }
    #             move.invoice_payments_widget = json.dumps(info, default=date_utils.json_default)
    #         else:
    #             move.invoice_payments_widget = json.dumps(False)


