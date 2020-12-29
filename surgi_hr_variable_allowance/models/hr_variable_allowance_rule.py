from odoo import models, fields, api


class HrVariableAllowanceRule(models.Model):
    _name = 'hr.variable.allowance.rule'

    name = fields.Char()
    code = fields.Char()

    allowance_type = fields.Selection([('fixed', 'Fixed'), ('rule', 'Rule')], default="fixed")
    allowance_or_deduction = fields.Selection([('allowance', 'Allowance'), ('deduction', 'Deduction')],
                                              default='allowance')
    rule = fields.Char()

    payslip_input_type_id = fields.Many2one('hr.payslip.input.type')
    salary_rule_id = fields.Many2one('hr.salary.rule')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Code already exists!'),
        ('name_unique', 'unique(name)', 'Name already exists!')
    ]
    
    @api.model
    def create(self, vals):
        res = super(HrVariableAllowanceRule, self).create(vals)

        input_type_id = self.env['hr.payslip.input.type'].create({
            'name': res.name + ' Variable allowance',
            'code': res.code
        })

        res.payslip_input_type_id = input_type_id.id
        return res

    def create_salary_rule(self):
        rule_code = """
result = 0
if payslip.input_line_ids:
   for it in payslip.input_line_ids:
       if it.input_type_id.code == '%s':
          result += it.amount 
"""
        if not self.salary_rule_id:
            salary_rule_id = self.env['hr.salary.rule'].create({
                'name': self.name,
                'category_id': self.env.ref('surgi_hr_variable_allowance.ALW').id if self.allowance_or_deduction == 'allowance' else self.env.ref('surgi_hr_variable_allowance.DED').id,
                'code': self.code,
                'sequence': 5,
                'struct_id': self.env.ref('surgi_hr_variable_allowance.variable_allowance_salary_structure').id,
                'active': True,
                'appears_on_payslip': True,
                'amount_select': 'code',
                'amount_python_compute':  rule_code % self.code
            })

            self.salary_rule_id = salary_rule_id.id
