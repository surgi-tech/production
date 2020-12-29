from datetime import date
from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models
# from dateutil.relativedelta import relativedelta

# =============== Dalia Atef =============
class operation_stage(models.Model):
    _name = 'operation.stage'
    _order = "sequence"

    # ==================== Methods =========================


    # ==================== Fields ==========================
    name = fields.Char('Visible Name', required=True)
    state_name = fields.Char('State Name', required=True)
    sequence = fields.Integer('Sequence', default=0)
    is_active = fields.Boolean('Active', default=True)
