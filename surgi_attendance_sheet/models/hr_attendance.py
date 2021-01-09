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


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    state = fields.Selection(
        selection=[('fixin', 'Fix In'), ('fixout', 'Fix Out'),
                   ('right', 'Right')],
        default='right')

    approval_state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('approved', 'Approved'),
                   ('reject', 'Rejected')],
        default='draft')

    def action_approve(self):
        for attendance in self:
            attendance.approval_state = 'approved'

    def action_reject(self):
        for attendance in self:
            attendance.approval_state = 'reject'

    @api.model
    def create(self, values):
        res = super(HrAttendance, self).create(values)
        if not res.employee_id.attendance_approval:
            res.approval_state = 'approved'
        return res

    def fix_attendance(self):
        self.write({'state': 'right'})
