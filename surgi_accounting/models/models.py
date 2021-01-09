from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class account_payment2(models.Model):
    _inherit = 'account.payment'

    ar_validate = fields.Boolean(string="AR Validation", )


    def action_draft(self):
        res =super(account_payment2, self).action_draft()
        print ('1111111111111111111111111111111111111111111111111111111111')
        self.ar_validate=False
        return res


    def ar_validation(self):
        print ('ARRRRRRRRRRRRRRRRRRRRRRRRRRRR')
        self.ar_validate = True

    def confirm_multi_payment(self):
        for record in self:
            if record.state == 'draft':
                record.ar_validation()

    def post2(self):
        # rec = super(account_payment2, self).post()
        # print ('rrrrrrrrrrrrrrrrrr',rec)
        # self.state = 'draft'
        # return rec
        #

        print ('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            rec.write({'state': 'draft'})

        #
        #     if rec.state != 'draft':
        #         raise UserError(_("Only a draft payment can be posted."))
        #
        #     if any(inv.state != 'posted' for inv in rec.invoice_ids):
        #         raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
        #
        #     # keep the name in case of a payment reset to draft
        #     if not rec.name:
        #         # Use the right sequence to set the name
        #         if rec.payment_type == 'transfer':
        #             sequence_code = 'account.payment.transfer'
        #         else:
        #             if rec.partner_type == 'customer':
        #                 if rec.payment_type == 'inbound':
        #                     sequence_code = 'account.payment.customer.invoice'
        #                 if rec.payment_type == 'outbound':
        #                     sequence_code = 'account.payment.customer.refund'
        #             if rec.partner_type == 'supplier':
        #                 if rec.payment_type == 'inbound':
        #                     sequence_code = 'account.payment.supplier.refund'
        #                 if rec.payment_type == 'outbound':
        #                     sequence_code = 'account.payment.supplier.invoice'
        #         rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
        #         if not rec.name and rec.payment_type != 'transfer':
        #             raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
        #
        #     moves = AccountMove.create(rec._prepare_payment_moves())
        #     moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
        #
        #     # Update the state / move before performing any reconciliation.
        #     move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
        #     rec.write({'state': 'draft', })
        #
        #     if rec.payment_type in ('inbound', 'outbound'):
        #         # ==== 'inbound' / 'outbound' ====
        #         if rec.invoice_ids:
        #             (moves[0] + rec.invoice_ids).line_ids \
        #                 .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id) \
        #                 .reconcile()
        #     elif rec.payment_type == 'transfer':
        #         # ==== 'transfer' ====
        #         moves.mapped('line_ids') \
        #             .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id) \
        #             .reconcile()

        return True



class NewModule(models.Model):
    _inherit = 'account.bank.statement.line'

    is_check = fields.Boolean(string="Check",default=False,compute="_compute_check")

    def _compute_check(self):
        for rec in self:
            if rec.journal_entry_ids:
                rec.is_check=True
            else:
                rec.is_check = False


class NewModule(models.Model):
    _inherit = 'account.bank.statement'

    total_check = fields.Float(string="UnReconcile Total",  required=False,compute='get_total_check' )


    @api.depends('line_ids')
    def get_total_check(self):
        total=0.0
        # print ('+++++++++++++++++++++++++++++++++++++++++',self.journal_id.account_balance)
        for rec in self.line_ids:
            if rec.is_check!=True:
                total+=rec.amount
        self.total_check=total



# class AccountJournal(models.Model):
#     _inherit = "account.journal"
#
#     def get_journal_dashboard_datas(self):
#         res =super(AccountJournal, self).get_journal_dashboard_datas()
#         print ('***********************************************SSSSSSSSSSSSSSSSSSSSSS')
#
#         return res