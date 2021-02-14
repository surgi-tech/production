from odoo import models, fields, api,_
from odoo.exceptions import UserError, Warning, ValidationError


class NewModule(models.Model):
    _inherit = 'account.move'

    seq_name = fields.Char(string="Exp Ref No.",)



class HRExpenseSheetInherit(models.Model):
    _inherit = 'hr.expense.sheet'


    seq_name = fields.Char(string="Exp Ref No.",)

    def action_sheet_move_create(self):
        res=super(HRExpenseSheetInherit, self).action_sheet_move_create()

        if self.account_move_id:
            self.account_move_id.seq_name=self.seq_name

        return res
class HRExpenseInherit(models.Model):
    _inherit = 'hr.expense'

    is_trusts = fields.Boolean(string="IS Trust",related='account_id.is_trusts'  )

    expense_type = fields.Selection(string="Expense Type", selection=[('direct_expense','Direct Expense'),
                                                                      ('trust', 'Trust'),('trust_recon', 'Trust Reconciliation') ])

    seq_name = fields.Char(string="Exp Ref No.",default='NEW')
    expense_reconciliation_id = fields.Many2one(comodel_name="hr.expense", string="Expense Reconciliation", )

    @api.onchange('expense_type')
    def filter_expense_reconciliation_id(self):
        lines=[]
        if self.expense_type=='trust_recon':
            for rec in self.env['hr.expense'].search([]):
                if rec.expense_type=='trust':
                    lines.append(rec.id)
            return {'domain': {'expense_reconciliation_id': [('id', 'in', lines)]}}



    @api.model_create_multi
    def create(self, values):
        for val in values:
            if 'expense_type' in val:
                if val['expense_type']=='direct_expense':
                    val['seq_name'] = self.env['ir.sequence'].next_by_code('direct.expense.sequence') or _('New')

                if val['expense_type']=='trust':
                    val['seq_name'] = self.env['ir.sequence'].next_by_code('trust.expense.sequence') or _('New')

                if val['expense_type']=='trust_recon':
                    val['seq_name'] = self.env['ir.sequence'].next_by_code('reconciliation.trust.expense.sequence') or _('New')



        # partners = super(HRExpenseInherit, self).create(values)
        # for partner in partners:
        #     if partner.customer_rank == 0 or partner.parent_id:
        #         for rec in self.env['ir.sequence'].search([]):
        #             if rec.code == 'library.card.number':
        #                 rec.number_next_actual -= 1
        #                 partner.ref = False
        #
        #             if rec.code in ['superMarket.cridit.number7', 'restaurants.cridit.number6', 'hotel.credit.number5',
        #                             'individuals.cash.number4', 'superMarket.cash.number3', 'li2.ca2.num2']:
        #
        #                 partner.ref = False
        #     else:
        #         partner.name = partner.name + "(" + str(partner.ref) + ")"


        res = super(HRExpenseInherit, self).create(values)
        return res


    def action_submit_expenses(self):
        res=super(HRExpenseInherit, self).action_submit_expenses()

        print("Resssssssbnnnnnnnsssss",res)
        x=''
        for rec in self:
            x  = str(x) + str(rec.seq_name)
            rec.sheet_id.seq_name = str(x)
        return res

    def _create_sheet_from_expenses(self):
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))

        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without product."))

        d=0
        t=0
        r=0
        for rec in self:
           if rec.expense_type=='direct_expense':
               d+=1
           if rec.expense_type=='trust':
               t+=1
           if rec.expense_type=='trust_recon':
               r+=1
        print('ddd',d,'ttttttt',t,'rrrrr',r)
        if d>=1 and (t == 0 and r==0) or t>=1 and (d == 0 and r==0) or r>=1 and (d == 0 and t==0):
           pass
        else:
            raise UserError(_("ooooooooooooooooooooooooooooooooooo"))




        todo = self.filtered(lambda x: x.payment_mode=='own_account') or self.filtered(lambda x: x.payment_mode=='company_account')
        sheet = self.env['hr.expense.sheet'].create({
            'company_id': self.company_id.id,
            'employee_id': self[0].employee_id.id,
            'name': todo[0].name if len(todo) == 1 else '',
            'expense_line_ids': [(6, 0, todo.ids)]
        })
        return sheet

class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    is_trusts = fields.Boolean(string="Trust Account",  )
# class ReportAccountHashIntegrity(models.AbstractModel):
#     _name = 'report.account.report_invoice_with_payments'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#
#         docs = self.env['hr.expense'].browse(docids)
#         print(docs,'JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ',docs)
#         return {
#             'doc_ids': docids,
#             'doc_model': 'hr.expense',
#             'docs': docs,
#         }