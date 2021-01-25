from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import formataddr


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    interviewer_1_survey = fields.Many2one('survey.survey', related='job_id.interviewer_1_survey')
    interviewer_1_response_id = fields.Many2one('survey.user_input', "Interviewer 1 Response", ondelete="set null")
    interviewer_1_user_id = fields.Many2one('res.users')

    interviewer_2_survey = fields.Many2one('survey.survey', related='job_id.interviewer_2_survey')
    interviewer_2_response_id = fields.Many2one('survey.user_input', "Interviewer 2 Response", ondelete="set null")
    interviewer_2_user_id = fields.Many2one('res.users')

    interviewer_3_survey = fields.Many2one('survey.survey', related='job_id.interviewer_3_survey')
    interviewer_3_response_id = fields.Many2one('survey.user_input', "Interviewer 2 Response", ondelete="set null")
    interviewer_3_user_id = fields.Many2one('res.users')

    accepted = fields.Boolean()
    shortlisted = fields.Boolean()
    to_gm = fields.Boolean()

    def action_start_interviewer_1_survey(self):
        self.ensure_one()
        if not self.interviewer_1_user_id or not (self.env.uid == self.interviewer_1_user_id.id):
            raise UserError("You are not allowed to answer this survey")
        # create a response and link it to this applicant
        if not self.interviewer_1_response_id:
            response = self.interviewer_1_survey._create_answer(user=self.interviewer_1_user_id)
            self.interviewer_1_response_id = response.id
        else:
            response = self.interviewer_1_response_id
        # grab the token of the response and start surveying
        return self.interviewer_1_survey.with_context(survey_token=response.access_token).action_start_survey(response)

    def action_print_interviewer_1_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.interviewer_1_response_id:
            return self.interviewer_1_survey.action_print_survey()
        else:
            response = self.interviewer_1_response_id
            return self.interviewer_1_survey.with_context(survey_token=response.access_token).action_print_survey(response)

    def action_start_interviewer_2_survey(self):
        self.ensure_one()
        if not self.interviewer_2_user_id or not (self.env.uid == self.interviewer_2_user_id.id):
            raise UserError("You are not allowed to answer this survey")
        # create a response and link it to this applicant
        if not self.interviewer_2_response_id:
            response = self.interviewer_2_survey._create_answer(user=self.interviewer_2_user_id)
            self.interviewer_2_response_id = response.id
        else:
            response = self.interviewer_2_response_id
        # grab the token of the response and start surveying
        return self.interviewer_2_survey.with_context(survey_token=response.access_token).action_start_survey(response)

    def action_print_interviewer_2_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.interviewer_2_response_id:
            return self.interviewer_2_survey.action_print_survey()
        else:
            response = self.interviewer_2_response_id
            return self.interviewer_2_survey.with_context(survey_token=response.access_token).action_print_survey(response)


    def action_start_interviewer_3_survey(self):
        self.ensure_one()
        if not self.interviewer_3_user_id or not (self.env.uid == self.interviewer_3_user_id.id):
            raise UserError("You are not allowed to answer this survey")
        # create a response and link it to this applicant
        if not self.interviewer_3_response_id:
            response = self.interviewer_3_survey._create_answer(user=self.interviewer_3_user_id)
            self.interviewer_3_response_id = response.id
        else:
            response = self.interviewer_3_response_id
        # grab the token of the response and start surveying
        return self.interviewer_3_survey.with_context(survey_token=response.access_token).action_start_survey(response)

    def action_print_interviewer_3_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.interviewer_3_response_id:
            return self.interviewer_3_survey.action_print_survey()
        else:
            response = self.interviewer_3_response_id
            return self.interviewer_3_survey.with_context(survey_token=response.access_token).action_print_survey(response)

    @api.constrains('stage_id')
    def send_updates_to_applicant(self):
        for rec in self:
            self.send_email_to_applicant(rec.email_from, rec)

    @api.model
    def send_email_to_applicant(self, applicant_email, application):
        email = self.env.user.work_email or self.env.user.email
        self.env['mail.mail'].create({
            'body_html': """Your Application have changed to stage %s.""" % application.stage_id.name,
            'state': 'outgoing',
            'email_from': formataddr((self.env.user.name, email)),
            'email_to': applicant_email,
            'subject': """New job Application update."""
        }).send()

    def action_makeMeeting(self):
        res = super(HrApplicant, self).action_makeMeeting()
        res['context'].update({
            'default_job_id': self.job_id.id,
            'default_responsible_id': self.user_id.id
        })
        return res
