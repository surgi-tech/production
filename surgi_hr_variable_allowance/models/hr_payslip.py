from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        variable_allowance = self.env['hr.variable.allowance.request'].search(
            [('employee_id', '=', res.employee_id.id),
             ('date', '>=', res.date_from),
             ('date', '<=', res.date_to)])

        data = {}
        for it in variable_allowance:
            tmp = data.get(it.rule_id.code, {})
            tmp = tmp.get('amount', 0) if tmp else 0
            data.update({
                it.rule_id.code: {
                    'amount': it.amount + tmp,
                    'input_type_id': it.rule_id.payslip_input_type_id.id
                }
            })

        for key in data:
            self.env['hr.payslip.input'].create({
                'input_type_id': data[key].get('input_type_id'),
                'amount': data[key].get('amount'),
                'payslip_id': res.id
            })

        return res
