# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrAttendancePenalty(models.Model):
    _name = "hr.attendance.penalty"

    TYPE = [('late', 'Late IN'),
            ('ab', 'Absence'),
            ('mis', 'Mis-Punch'),
            ('diff', 'Early Out')]

    name = fields.Char('Name', required=True)
    date = fields.Date('Penalty Date', required=True)
    accrual_date = fields.Date('Accrual Date', required=True)
    paid = fields.Boolean(string="Paid", default=False, )
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    sheet_id = fields.Many2one('attendance.sheet', 'Attendance Sheet',
                               readonly=True)
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', readonly=True)
    type = fields.Selection(string="Type", selection=TYPE, required=True, )
    amount = fields.Float('Amount')