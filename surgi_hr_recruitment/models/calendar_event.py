from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    job_id = fields.Many2one('hr.job')
    responsible_id = fields.Many2one('res.users')
