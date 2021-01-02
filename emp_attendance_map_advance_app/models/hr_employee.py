# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allow_check_in_description = fields.Boolean(default=False)
    allow_check_in_task = fields.Boolean(default=False)


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    allow_check_in_description = fields.Boolean(default=False)
    allow_check_in_task = fields.Boolean(default=False)
