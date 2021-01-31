from odoo import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    overtime_budget = fields.Float()
