
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class payment_register_surgi(models.TransientModel):
    _inherit = 'account.payment.register'

    check_number = fields.Char(string="Check Number", readonly=False, copy=False,requiredcre=True,
                               help="Number of the check corresponding to this payment. If your pre-printed check are not already numbered, "
                                    "you can manage the numbering in the journal configuration page.")

    date_due = fields.Date('Due Date', required=True)
    collection_receipt_number = fields.Integer(string="Receipt Number")
    collection_rep = fields.Many2one('res.users', 'Collection Rep', track_visibility='onchange')
    collection_rep_name = fields.Char(string="Collection Rep", track_visibility='onchange')
    # second_approval = fields.Boolean("Second Approval")

    def create_payments(self):

        print("444444444444444444444444444444444444444444444")
        Payment = self.env['account.payment']
        payments = Payment.create(self.get_payments_vals())
        # payments.post2()
        # print(payments.post2())
        for pay in payments:
            pay.check_number=self.check_number
            pay.date_due=self.date_due
            pay.collection_receipt_number=self.collection_receipt_number
            pay.collection_rep=self.collection_rep
            pay.collection_rep_name=self.collection_rep_name

            print(pay.check_number,self.check_number,'888888888888888888888888888888888888888')



        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals
