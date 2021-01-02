# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.constrains('request_date_from')
    def _check_leave_limit(self):
        for req in self:
            if req.holiday_status_id.flag_monthly_limit:
                leave_ids = self.env['hr.leave'].search(
                    [('employee_id', '=', req.employee_id.id),
                     ('holiday_status_id', '=', req.holiday_status_id.id),
                     ('state', '=', 'validate')])
                if leave_ids:
                    current_leave_date = req.request_date_from
                    current_leave_year = int(current_leave_date.year)
                    current_leave_month = int(current_leave_date.month)
                    leave_days = 0.00
                    remaining = 0.00
                    for leave in leave_ids:
                        leave_date = leave.request_date_from
                        year = int(leave_date.year)
                        month = int(leave_date.month)
                        if year == current_leave_year and \
                                        month == current_leave_month:
                            leave_days += leave.number_of_days_display
                    remaining = req.holiday_status_id.leave_limit_days - \
                                float(leave_days)
                    if float(req.number_of_days_display) > float(remaining):
                        raise ValidationError(
                            _("You Monthly Leave Limit is : %s\nYou have "
                              "already taken %s leaves in this month\nNow your "
                              "remaining leaves are :  %s") %
                            (req.holiday_status_id.leave_limit_days,
                             float(leave_days),
                             float(remaining)))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: