from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    interviewer_1_survey = fields.Many2one('survey.survey')
    interviewer_2_survey = fields.Many2one('survey.survey')
    interviewer_3_survey = fields.Many2one('survey.survey')

    def action_print_interviewer_1_survey(self):
        return self.interviewer_1_survey.action_print_survey()

    def action_print_interviewer_2_survey(self):
        return self.interviewer_2_survey.action_print_survey()

    def action_print_interviewer_3_survey(self):
        return self.interviewer_3_survey.action_print_survey()
