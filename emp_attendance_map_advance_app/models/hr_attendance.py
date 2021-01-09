# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    allow_check_in_description = fields.Boolean(related='employee_id.allow_check_in_description')
    allow_check_in_task = fields.Boolean(related='employee_id.allow_check_in_task')
    task_description = fields.Text(string="", required=False, )
    task_id = fields.Many2one(comodel_name="project.task", string="", required=False, )
