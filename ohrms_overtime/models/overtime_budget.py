from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DepartmentBudget(models.Model):
    _name = 'overtime.department.budget'

    budget_id = fields.Many2one("overtime.budget")
    department_id = fields.Many2one("hr.department")
    amount = fields.Float()
    consumed_amount = fields.Float()

    _sql_constraints = [
        ('budget_unique', 'unique(budget_id, department_id)', 'Can not have multiple department in the same budget.'),
    ]

    @api.constrains('consumed_amount')
    def _check_exceeds_amount(self):
        for rec in self:
            if rec.consumed_amount > rec.amount:
                raise ValidationError("Have exceeds the department '%(department_name)s' budget." % {"department_name": rec.department_id.name})


class EmployeeBudget(models.Model):
    _name = 'overtime.employee.budget'

    budget_id = fields.Many2one("overtime.budget")
    employee_id = fields.Many2one("hr.employee")
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
    amount = fields.Float()
    consumed_amount = fields.Float()

    _sql_constraints = [
        ('budget_unique', 'unique(budget_id, employee_id)', 'Can not have multiple employee in the same budget.'),
    ]

    @api.constrains('consumed_amount')
    def _check_exceeds_amount(self):
        for rec in self:
            if rec.consumed_amount > rec.amount:
                raise ValidationError("Have exceeds the employee '%(employee_name)s' budget." % {"employee_name": rec.employee_id.name})


class OvertimeBudget(models.Model):
    _name = 'overtime.budget'

    name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()

    company_budget = fields.Float()
    consumed_budget = fields.Float()
    departments_budget = fields.One2many("overtime.department.budget", "budget_id")
    employees_budget = fields.One2many("overtime.employee.budget", "budget_id")

    status = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('end', 'End')], default='draft')

    request_ids = fields.One2many("hr.overtime", "budget_id")

    def auto_fill_department_budget(self):
        departments = self.env['hr.department'].search([])

        linked_departments = self.env['overtime.department.budget'].search([('budget_id', '=', self.id)])
        for it in linked_departments:
            it.unlink()

        for dep in departments:
            self.env['overtime.department.budget'].create({
                'department_id': dep.id,
                'amount': dep.overtime_budget,
                'budget_id': self.id
            })

    def auto_fill_employee_budget(self):
        employees = self.env['hr.employee'].search([])

        linked_employees = self.env['overtime.employee.budget'].search([('budget_id', '=', self.id)])
        for it in linked_employees:
            it.unlink()

        for emp in employees:
            self.env['overtime.employee.budget'].create({
                'employee_id': emp.id,
                'amount': emp.overtime_budget,
                'budget_id': self.id
            })

    @api.constrains('consumed_budget')
    def _check_exceed_budget(self):
        for rec in self:
            if rec.company_budget > rec.company_budget:
                raise ValidationError("Have exceeded the company's budget %(name)s" % {"name": rec.name})

    @api.constrains('status')
    def _check_valid_budgets(self):
        for rec in self:
            if rec.status != 'draft':
                departments_budget = {}
                employee_departments_budget = {}
                company_budget = rec.company_budget

                total_departments_budget = 0
                for dep in rec.departments_budget:
                    if dep.department_id.id not in departments_budget:
                        departments_budget.update({dep.department_id.id: dep.amount})
                    else:
                        departments_budget[dep.department_id.id] += dep.amount

                    total_departments_budget += dep.amount

                if total_departments_budget > company_budget:
                    raise ValidationError("Departments Budget can not Exceed the Company budget.")

                # Get employees budget aggregated by department.
                for emp in rec.employees_budget:
                    if emp.department_id.id not in employee_departments_budget:
                        employee_departments_budget.update({emp.department_id.id: emp.amount})
                    else:
                        employee_departments_budget[emp.department_id.id] += emp.amount

                # Checking aggregated employees budget by department with departments configuration.
                for key, value in employee_departments_budget.items():
                    if key in departments_budget:
                        _allowed_budget = departments_budget.get(key)
                        if value > _allowed_budget:
                            _department_name = self.env['hr.department'].browse(key).name
                            raise ValidationError("Total budget '%(total_budget)s' configured for Employees "
                                                  "in this department '%(department)s',"
                                                  " is exceeding the allowed budget '%(allowed_budget)s'" %
                                                  {"department": _department_name, "total_budget": value, "allowed_budget": _allowed_budget})
                    else:
                        raise ValidationError("This department %s has no budget configured in department budget section." % key)

            elif rec.status == 'draft' and rec.request_ids:
                raise ValidationError("Can not get back to draft state since there are requests registered to this budget.")


