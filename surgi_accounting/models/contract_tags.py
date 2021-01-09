from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class NewModule(models.Model):
    _inherit = 'hr.contract'

    analytic_tags = fields.Many2one(comodel_name="account.analytic.tag", string="Analytic Tags",)
