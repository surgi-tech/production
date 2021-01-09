from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrVariableAllowanceRequest(models.Model):
    _name = 'hr.variable.allowance.request'

    name = fields.Char()
    date = fields.Date()
    tmp_amount = fields.Float(compute='_compute_amount', store=True)
    amount_rate_multiplier = fields.Float(default=1.0)
    amount = fields.Float()

    rule_id = fields.Many2one('hr.variable.allowance.rule')
    rule_id_allowance_type = fields.Selection(related='rule_id.allowance_type', store=False)
    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    payslip_id = fields.Many2one('hr.payslip')

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id
        else:
            self.contract_id = False

    @api.depends('contract_id', 'rule_id', 'amount_rate_multiplier')
    def _compute_amount(self):
        for rec in self:
            if rec.employee_id and rec.contract_id and rec.rule_id and rec.rule_id.allowance_type == 'rule':
                try:
                    rec.tmp_amount = rec.amount_rate_multiplier * eval(rec.rule_id.rule, {'contract': rec.contract_id, 'employee': rec.employee_id})
                    if rec.rule_id.allowance_or_deduction == 'deduction':
                        rec.tmp_amount = abs(rec.tmp_amount) * -1
                    rec.amount = rec.tmp_amount
                except:
                    raise ValidationError("Wrong rule's syntax, please fix it and try again.")
            else:
                rec.tmp_amount = 0

    def write(self, vals):
        if self.rule_id.allowance_or_deduction == 'deduction':
            amount = vals.get('amount', None)
            if amount:
                vals['amount'] = abs(amount) * -1
        res = super(HrVariableAllowanceRequest, self).write(vals)
        return res
