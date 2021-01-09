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


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    penalty_ids = fields.Many2many(comodel_name='hr.attendance.penalty',
                                   string='Penalties')
    penalty_amount = fields.Float('Total Penalties',
                                  compute='_compute_penalty_total_amount')

    def _compute_penalty_total_amount(self):
        for slip in self:
            slip.penalty_amount = sum([p.amount for p in slip.penalty_ids])

    def action_get_penalty(self):
        for slip in self:
            if slip.date_from and slip.date_to and slip.employee_id:
                penalty_ids = self.env['hr.attendance.penalty'].search(
                    [('accrual_date', '>=', slip.date_from),
                     ('accrual_date', '<=', slip.date_to),
                     ('paid', '=', False),
                     ('employee_id', '=', slip.employee_id.id)])
                if penalty_ids:
                    slip.penalty_ids = [(6, 0, penalty_ids.ids)]

    def action_payslip_done(self):
        res = super(HrPayslip,self).action_payslip_done()
        for slip in self:
            if slip.penalty_ids:
                for pen in self.penalty_ids:
                    pen.paid = True
        return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from',
                  'date_to')
    def _onchange_employee(self):
        self.action_get_penalty()
        return super(HrPayslip, self)._onchange_employee()
