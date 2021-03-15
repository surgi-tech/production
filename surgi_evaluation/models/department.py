from odoo import models, fields, api
class EvaluationDepartment(models.Model):
    _name = 'evaluation.department'
    _rec_name = 'name'

    name = fields.Char()

