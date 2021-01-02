# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    flag_monthly_limit = fields.Boolean(string="Monthly Leave Limit")
    leave_limit_days = fields.Float(string="Leave Limit Days")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: