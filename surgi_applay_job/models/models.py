from odoo import models, fields, api

class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    address = fields.Char(string="Address", required=False, )
    qualification = fields.Char(string="Qualification", required=False, )
    training_courses = fields.Text(string="Training Courses", required=False, )
    previous_experience = fields.Text(string="Previous Experience ", required=False, )
    age = fields.Char(string="Age ", required=False, )
    gender= fields.Selection(string="Gender", selection=[('Male', 'Male'), ('Female', 'Female'), ], required=False, )
    nominee = fields.Char(string="Nominee", required=False, )