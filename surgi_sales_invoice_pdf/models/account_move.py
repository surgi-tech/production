from odoo import models, fields, api, _
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = num2words(invoice.amount_total, lang='ar')

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")
    partner_arabic_name = fields.Char(compute='_set_partner_arabic_name', store=True)
    related_operation = fields.Char(related='operation_id.name', store=True)

    @api.depends('partner_id')
    def _set_partner_arabic_name(self):
        for rec in self:
            if hasattr(rec.partner_id, "arabic_name"):
                rec.partner_arabic_name = rec.partner_id.arabic_name
            else:
                rec.partner_arabic_name = ""

