
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo import tools, _
import time
import babel
import logging



class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    sin_exist = fields.Boolean("Has Social Insurance")
    registration_number = fields.Char('Registration Number of the Employee', groups="hr.group_hr_user", copy=False)
    sin_no = fields.Char("Social Insurance No",track_visibility='onchange')
    sin_date = fields.Date("Social Insurance Start Date",track_visibility='onchange')
    sin_end_date = fields.Date("Social Insurance End Date",track_visibility='onchange')
    sin_title = fields.Char(string="Social Job Title",track_visibility='onchange')
    mi_exist = fields.Boolean("Has Medical Insurance",track_visibility='onchange')
    mi_company = fields.Selection(string="Medical Co.", selection=[('inaya', 'Inaya')])
    mi_no = fields.Char(string="Medical Insurance NO", help='Medical  Insurance No',track_visibility='onchange')
    mi_date = fields.Date(string="Medical Insurance Date", help='Medical  Insurance Date',track_visibility='onchange')
    sin_basic_salary = fields.Float(string="Basic Salary SIN", digits=dp.get_precision('Payroll'),track_visibility='onchange')
    sin_variable_salary = fields.Float(string="Variable Salary SIN", digits=dp.get_precision('Payroll'),track_visibility='onchange')
    allowances = fields.Float(string="Allowances", digits=dp.get_precision('Payroll'),track_visibility='onchange')
    prev_raise = fields.Float(string="previous Annual Raises", digits=dp.get_precision('Payroll'),track_visibility='onchange')

    wage = fields.Monetary('Wage', required=True, tracking=True, help="Employee's monthly gross wage.",compute='calculate_wage')

    @api.depends('basic_salary','basic_salary_precent')
    def calculate_wage(self):
        self.wage=0
        for rec in self:
            rec.wage = rec.basic_salary + rec.basic_salary_precent


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.registration_number = self.employee_id.registration_number


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    employee_code = fields.Char(string="Employee Code", related='employee_id.registration_number', readonly=True)
    grade_id = fields.Many2one('grade.grade', related='employee_id.contract_id.grade_id', readonly=True)
    rank_id = fields.Many2one('rank.rank', related='employee_id.contract_id.rank_id', readonly=True)
    rang_id = fields.Many2one('rang.rang', related='employee_id.contract_id.rang_id', readonly=True)