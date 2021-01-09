from odoo import models, fields, api, _


class EssHrSurvey(models.Model):
    _name = 'ess.hr.survey'

    name = fields.Char()
    survey_link = fields.Char()
    survey_id = fields.Many2one('survey.survey')

