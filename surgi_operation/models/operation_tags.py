from odoo import fields, models, api, exceptions
from odoo.exceptions import  Warning


class operation_tag(models.Model):
    _name= "operation.tag"

    # ================== fields ===================
    name = fields.Char('Tag')