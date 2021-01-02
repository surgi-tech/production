from odoo import models, fields, api

class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    count_man_employee = fields.Integer(string="Counter",compute='calculate_count_manger_employee')
    # @api.depends('parent_id')
    def calculate_count_manger_employee(self):
        self.count_man_employee=0
        employee_rec=self.env['hr.employee'].search([])
        for rec in self.search([]):
            count = 0
            for man in employee_rec:
                print(rec.id,man.parent_id.id,)
                if rec.id == man.parent_id.id:
                    count += 1

            rec.count_man_employee = count

