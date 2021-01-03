from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    left_logo = fields.Binary()
    right_logo = fields.Binary()
