from odoo import models, fields, api
class ApprovalRequestInherit(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one(comodel_name="hr.department", string="Department",compute='get_related_employee_date',store=True)
    job_title = fields.Char(string="Job Title", required=False,compute='get_related_employee_date',store=True )
    registration_number = fields.Char(string="Registration Number of the Employee",compute='get_related_employee_date',store=True )

    @api.depends('request_owner_id')
    def get_related_employee_date(self):
       self.department_id=False
       self.job_title=''
       self.registration_number=''
       employee_record=self.env['hr.employee']
       for rec in self:
           for emp in employee_record.search([('user_id','=',rec.request_owner_id.id)]):
               rec.department_id=emp.department_id.id
               rec.job_title=emp.job_title
               rec.registration_number=emp.registration_number