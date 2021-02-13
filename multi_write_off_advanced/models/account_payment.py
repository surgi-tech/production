# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')], default='full',
        required=True, string='Payment Option')
    amount_pay_total = fields.Float('Amount Total', readonly=1)
    # amount = fields.Float('Payment Amount', readonly=1)
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.multi', 'register_id', string='Write Off Accounts')

    @api.model
    def default_get(self, fields):
        rec = super(payment_register, self).default_get(fields)
        amount_pay_total = 0
        context = self._context
        if context.get('active_ids'):
            for inv in context.get('active_ids'):
                record = self.env['account.move'].browse(inv)
                amount_pay_total += record.amount_total
            rec.update({
                'amount_pay_total': amount_pay_total,
                'amount': amount_pay_total,
            })
        return rec

    @api.onchange('writeoff_multi_acc_ids')
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount_payment for line in self.writeoff_multi_acc_ids])
            self.amount = self.amount_pay_total - diff_amount

    def _prepare_payment_vals(self, invoices):
        res = super(payment_register, self)._prepare_payment_vals(invoices)
        if self.writeoff_multi_acc_ids:
            multi_accounts = []
            diff_amount = 0.0
            amount = res.get('amount')
            for line in self.writeoff_multi_acc_ids:
                write_off_percent = round(line.amount_payment / self.amount_pay_total,
                                          2) if self.amount_pay_total else 0
                write_off_amount = round(amount * write_off_percent, 2)
                multi_accounts.append((0, 0, {'writeoff_account_id': line.writeoff_account_id.id,
                                              'name': line.name or '',
                                              'amt_percent': line.amt_percent or '',
                                              'amount': write_off_amount,
                                              'currency_id': line.currency_id and line.currency_id.id or ''}))
                diff_amount += write_off_amount

            amount = round(amount - diff_amount, 2)
            res.update({
                'payment_option': 'partial',
                'payment_difference_handling': 'reconcile',
                'post_diff_acc': 'multi',
                'amount': amount,
                'payment_difference': round(diff_amount, 2),
                'writeoff_multi_acc_ids': multi_accounts
            })
        return res

    def _create_payment_vals_from_wizard(self):
        res =super(payment_register, self)._create_payment_vals_from_wizard()
        if not self.currency_id.is_zero(self.payment_difference) and self.post_diff_acc == 'multi':
            write_off_vals = []
            for woff_payment in self.writeoff_multi_acc_ids:
                write_off_vals.append({
                    'name': woff_payment.name,
                    'amount': woff_payment.amount_payment or 0.0,
                    'account_id': woff_payment.writeoff_account_id.id,
                    'is_multi_write_off': True
                })
            res['multi_write_off_line_vals'] = write_off_vals
        return res


class account_payment(models.Model):
    _inherit = "account.payment"

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')], default='full',
        required=True, string='Payment Option')
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_id', string='Write Off Accounts')

    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'

    @api.onchange('writeoff_multi_acc_ids')
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            self.amount = self.invoice_ids and self.invoice_ids[0].amount_residual - diff_amount

    @api.model_create_multi
    def create(self, vals_list):
        write_off_line_vals_list = []
        for vals in vals_list:
            # Hack to add a custom write-off line.
            # write_off_line_vals_list.append()
            context = self._context.copy()
            if context.get('woff_params'):
                context['woff_params'].update(vals.pop('multi_write_off_line_vals', None))
            else:
                context['woff_params'] = vals.pop('multi_write_off_line_vals', None)
            self.env.context = context
        return super(account_payment, self).create(vals_list)

    def post(self):
        for move in self:
            if move.payment_difference_handling == 'reconcile' and move.post_diff_acc == 'multi':
                amount = 0
                for payment in move.writeoff_multi_acc_ids:
                    amount += payment.amount
                if move.amount > amount:
                    if move.payment_type == 'inbound' and round(move.payment_difference, 2) != round(amount, 2):
                        raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
                    elif move.payment_type == 'outbound' and round(move.payment_difference, 2) != -round(amount, 2):
                        raise UserError(_("The sum of write off amounts and payment difference amounts are not equal."))
        return super(account_payment, self).post()

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))
        # Compute amounts.
        write_off_amount = write_off_line_vals.get('amount', 0.0)
        woff_params = self._context.get('woff_params')
        if woff_params:
            multi_write_off_amount = 0
            for rec in woff_params:
                multi_write_off_amount += rec.get('amount')
            write_off_amount = multi_write_off_amount

        if self.payment_type == 'inbound':
            # Receive money.
            counterpart_amount = -self.amount
            write_off_amount *= -1
        elif self.payment_type == 'outbound':
            # Send money.
            counterpart_amount = self.amount
        else:
            counterpart_amount = 0.0
            write_off_amount = 0.0

        balance = self.currency_id._convert(counterpart_amount, self.company_id.currency_id, self.company_id, self.date)
        counterpart_amount_currency = counterpart_amount
        write_off_balance = self.currency_id._convert(write_off_amount, self.company_id.currency_id, self.company_id, self.date)
        write_off_amount_currency = write_off_amount
        currency_id = self.currency_id.id
        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )
        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': -counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': balance < 0.0 and -balance or 0.0,
                'credit': balance > 0.0 and balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_debit_account_id.id if balance < 0.0 else self.journal_id.payment_credit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency + write_off_amount_currency if currency_id else 0.0,
                'currency_id': currency_id,
                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        if write_off_balance:
            # Write-off line.
            if woff_params:
                for rec in woff_params:
                    write_off_balance = self.currency_id._convert(rec.get('amount'), self.company_id.currency_id,
                                                                  self.company_id, self.date)
                    write_off_amount_currency = rec.get('amount')
                    if self.payment_type == 'inbound':
                        # Receive money.
                        write_off_balance *= -1
                    line_vals_list.append({
                        'name': rec.get('name') or default_line_name,
                        'amount_currency': -write_off_amount_currency,
                        'currency_id': currency_id,
                        'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                        'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                        'partner_id': self.partner_id.id,
                        'account_id': rec.get('account_id'),
                    })
        return line_vals_list

    # def _prepare_payment_moves(self):
    #     if not self.post_diff_acc == 'multi':
    #         return super(account_payment, self)._prepare_payment_moves()
    #     all_move_vals = []
    #     for payment in self:
    #         company_currency = payment.company_id.currency_id
    #         move_names = payment.move_name.split(
    #             payment._get_move_name_transfer_separator()) if payment.move_name else None
    #
    #         write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
    #         if payment.payment_type in ('outbound', 'transfer'):
    #             counterpart_amount = payment.amount
    #             liquidity_line_account = payment.journal_id.default_debit_account_id
    #         else:
    #             counterpart_amount = -payment.amount
    #             liquidity_line_account = payment.journal_id.default_credit_account_id
    #
    #         if payment.currency_id == company_currency:
    #             balance = counterpart_amount
    #             write_off_balance = write_off_amount
    #             counterpart_amount = write_off_amount = 0.0
    #             currency_id = False
    #         else:
    #             balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id,
    #                                                    payment.payment_date)
    #             write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id,
    #                                                              payment.payment_date)
    #             currency_id = payment.currency_id.id
    #
    #         if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
    #             liquidity_line_currency_id = payment.journal_id.currency_id.id
    #             liquidity_amount = company_currency._convert(
    #                 balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
    #         else:
    #             liquidity_line_currency_id = currency_id
    #             liquidity_amount = counterpart_amount
    #
    #         rec_pay_line_name = ''
    #         if payment.payment_type == 'transfer':
    #             rec_pay_line_name = payment.name
    #         else:
    #             if payment.partner_type == 'customer':
    #                 if payment.payment_type == 'inbound':
    #                     rec_pay_line_name += _("Customer Payment")
    #                 elif payment.payment_type == 'outbound':
    #                     rec_pay_line_name += _("Customer Credit Note")
    #             elif payment.partner_type == 'supplier':
    #                 if payment.payment_type == 'inbound':
    #                     rec_pay_line_name += _("Vendor Credit Note")
    #                 elif payment.payment_type == 'outbound':
    #                     rec_pay_line_name += _("Vendor Payment")
    #             if payment.invoice_ids:
    #                 rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))
    #
    #         if payment.payment_type == 'transfer':
    #             liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
    #         else:
    #             liquidity_line_name = payment.name
    #         move_vals = {
    #             'date': payment.payment_date,
    #             'ref': payment.communication,
    #             'journal_id': payment.journal_id.id,
    #             'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
    #             'partner_id': payment.partner_id.id,
    #             'line_ids': [
    #                 (0, 0, {
    #                     'name': rec_pay_line_name,
    #                     'amount_currency': counterpart_amount + write_off_amount,
    #                     'currency_id': currency_id,
    #                     'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
    #                     'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
    #                     'date_maturity': payment.payment_date,
    #                     'partner_id': payment.partner_id.id,
    #                     'account_id': payment.destination_account_id.id,
    #                     'payment_id': payment.id,
    #                 }),
    #                 (0, 0, {
    #                     'name': liquidity_line_name,
    #                     'amount_currency': -liquidity_amount,
    #                     'currency_id': liquidity_line_currency_id,
    #                     'debit': balance < 0.0 and -balance or 0.0,
    #                     'credit': balance > 0.0 and balance or 0.0,
    #                     'date_maturity': payment.payment_date,
    #                     'partner_id': payment.partner_id.id,
    #                     'account_id': liquidity_line_account.id,
    #                     'payment_id': payment.id,
    #                 }),
    #             ],
    #         }
    #         if write_off_balance:
    #             for woff_payment in self.writeoff_multi_acc_ids:
    #                 write_off_amount = payment.payment_difference_handling == 'reconcile' and -woff_payment.amount or 0.0
    #                 if payment.currency_id == company_currency:
    #                     write_off_balance = write_off_amount
    #                 else:
    #                     write_off_balance = payment.currency_id._convert(write_off_amount, company_currency,
    #                                                                      payment.company_id,
    #                                                                      payment.payment_date)
    #                 move_vals['line_ids'].append((0, 0, {
    #                     'name': woff_payment.name,
    #                     'amount_currency': -write_off_amount,
    #                     'currency_id': currency_id,
    #                     'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
    #                     'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
    #                     'date_maturity': payment.payment_date,
    #                     'partner_id': payment.partner_id.id,
    #                     'account_id': woff_payment.writeoff_account_id.id,
    #                     'payment_id': payment.id,
    #                 }))
    #         if move_names:
    #             move_vals['name'] = move_names[0]
    #
    #         all_move_vals.append(move_vals)
    #
    #         if payment.payment_type == 'transfer':
    #
    #             if payment.destination_journal_id.currency_id:
    #                 transfer_amount = payment.currency_id._convert(counterpart_amount,
    #                                                                payment.destination_journal_id.currency_id,
    #                                                                payment.company_id, payment.payment_date)
    #             else:
    #                 transfer_amount = 0.0
    #
    #             transfer_move_vals = {
    #                 'date': payment.payment_date,
    #                 'ref': payment.communication,
    #                 'partner_id': payment.partner_id.id,
    #                 'journal_id': payment.destination_journal_id.id,
    #                 'line_ids': [
    #                     (0, 0, {
    #                         'name': payment.name,
    #                         'amount_currency': -counterpart_amount,
    #                         'currency_id': currency_id,
    #                         'debit': balance < 0.0 and -balance or 0.0,
    #                         'credit': balance > 0.0 and balance or 0.0,
    #                         'date_maturity': payment.payment_date,
    #                         'partner_id': payment.partner_id.id,
    #                         'account_id': payment.company_id.transfer_account_id.id,
    #                         'payment_id': payment.id,
    #                     }),
    #                     (0, 0, {
    #                         'name': _('Transfer from %s') % payment.journal_id.name,
    #                         'amount_currency': transfer_amount,
    #                         'currency_id': payment.destination_journal_id.currency_id.id,
    #                         'debit': balance > 0.0 and balance or 0.0,
    #                         'credit': balance < 0.0 and -balance or 0.0,
    #                         'date_maturity': payment.payment_date,
    #                         'partner_id': payment.partner_id.id,
    #                         'account_id': payment.destination_journal_id.default_credit_account_id.id,
    #                         'payment_id': payment.id,
    #                     }),
    #                 ],
    #             }
    #             if move_names and len(move_names) == 2:
    #                 transfer_move_vals['name'] = move_names[1]
    #             all_move_vals.append(transfer_move_vals)
    #     return all_move_vals


class writeoff_accounts(models.Model):
    _name = 'writeoff.accounts'

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_id = fields.Many2one('account.payment', string='Payment Record')

    @api.onchange('amt_percent')
    def _onchange_amt_percent(self):

        if self.amt_percent and self.amt_percent > 0:
            if self.payment_id.invoice_ids:
                self.amount = self.payment_id.invoice_ids[0].amount_total * self.amt_percent / 100


class RegisterWriteoffMulti(models.TransientModel):
    _name = 'writeoff.multi'

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount_payment = fields.Monetary(string='Payment Amount', required=True, )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    register_id = fields.Many2one('account.payment.register', string='Register Record')

    @api.onchange('amt_percent')
    def _onchange_amt_percent(self):
        if self.amt_percent and self.amt_percent > 0:
            if self.register_id.amount_pay_total:
                self.amount_payment = self.register_id.amount_pay_total * self.amt_percent / 100
