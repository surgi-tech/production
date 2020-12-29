from odoo import models, fields, api, _


class SurveyInvite(models.TransientModel):
    _inherit = 'survey.invite'

    def send_to_ess(self):
        for rec in self:
            ess_record = self.env['ess.hr.survey'].search([('survey_id', '=', rec.survey_id.id)])
            if not ess_record:
                self.env['ess.hr.survey'].create({
                    'name': rec.survey_id.display_name,
                    'survey_link': rec.survey_start_url,
                    'survey_id': rec.survey_id.id
                })
