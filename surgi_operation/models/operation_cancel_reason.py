from odoo import fields, models, api, exceptions
from odoo.exceptions import  Warning


class operation_cancel_reason(models.Model):
    _name= "operation.cancel.reason"

    # ================== fields ===================
    name = fields.Char('Reason')