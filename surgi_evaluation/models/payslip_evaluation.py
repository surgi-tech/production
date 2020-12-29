from odoo import models, fields, api, _
class NewModule(models.Model):
    _inherit = 'hr.payslip'

    total_evaluation = fields.Float(string="Total Evaluation",compute='_compute_total_evaluation')
    #
    @api.depends('employee_id','date_from','date_to')
    def _compute_total_evaluation(self):

        # for rec in self:
        evaluation_rec=self.env['evaluation.evaluation'].search([('employee_id','=',self.employee_id.id),('date_start','>=',self.date_from),('date_start','<=',self.date_to)])
        total=0.0
        for rec in evaluation_rec:
            total+=rec.total_totals
        self.total_evaluation=total