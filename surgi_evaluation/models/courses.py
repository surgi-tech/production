from odoo import models, fields, api
class CoursesName(models.Model):
    _name = 'courses.name'
    _rec_name = 'name'

    name = fields.Char()
    type = fields.Selection(string="Type", selection=[('Technical', 'Technical'), ('Soft', 'Soft'), ], required=False, )
    cost = fields.Float(string="Cost",  required=False, )