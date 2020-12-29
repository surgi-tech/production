from odoo import models, fields, api, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    job_id = fields.Many2one('hr.job', related='employee_id.job_id')
