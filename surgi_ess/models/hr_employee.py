from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def action_unfollow(self):
        pass
