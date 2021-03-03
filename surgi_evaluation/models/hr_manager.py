from odoo import models, fields, api
class HRManagerEvaluation(models.Model):
    _name = 'hr.manager.evaluation'
    _rec_name = 'employee_id'
    _description = 'New Description'
    employee_relation_id = fields.Many2one(comodel_name="evaluation.evaluation", string="Employee", required=False, )

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    performance= fields.Selection(string="Performance",
                                  selection=[('Exceed', 'Exceed'),
                                             ('Meet', 'Meet'),
                                             ('PIP', 'PIP'),
                                             ('PAP', 'PAP'),

                                             ],
                                  required=False, )

    pip_type = fields.Selection(string="PIP", selection=[('pip_soft', 'TNA Soft skills'),
                                             ('pip_technical', 'TNA Technical'),
                                             ('soft_technical', 'TNA Technical & Soft skills'),], required=False, )

    course_id = fields.Many2many(comodel_name="courses.name", string="Course", required=False, )


    replacement = fields.Boolean(string="Replacement",  )
    termination_date = fields.Date(string="Termination Date", required=False, )

    job_title = fields.Char(string="Job Title",related='employee_id.job_title' )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",related='employee_id.department_id' )
    section_id = fields.Many2one(comodel_name="hr.department", string="Section",related='employee_id.section_id'  )
    registration_number = fields.Char(string="Registration Number of the Employee",
                                      related='employee_id.registration_number')

    is_department_man = fields.Boolean(string="", compute='check_if_department_manager')

    grade_id = fields.Many2one(comodel_name="grade.grade", string="Grade",)
    rank_id = fields.Many2one(comodel_name="rank.rank", string="Rank",)
    rang_id = fields.Many2one(comodel_name="rang.rang", string="Range",)

    date_start = fields.Date(string="Start Date", required=False, )
    date_end = fields.Date(string="End Date", required=False, )


    @api.onchange('employee_id')
    def get_employee_grad(self):
        self.grade_id=self.employee_id.grade_id.id
        self.rank_id=self.employee_id.rank_id.id
        self.rang_id=self.employee_id.rang_id.id



    @api.depends('is_department_man', 'employee_id')
    def check_if_department_manager(self):
        self.is_department_man = False
        for rec in self:
            if self.env.user.id == rec.employee_id.parent_id.user_id.id:
                rec.is_department_man = True

            else:
                rec.is_department_man = False

    @api.onchange('employee_relation_id','employee_id')
    def filters_employee_manager(self):
        categ_ids = []
        employee_rec = self.env['hr.employee'].search([])
        for emp in employee_rec:
            if emp.parent_id.user_id == self.env.user and not self.env.user.has_group('surgi_evaluation.all_permission_group_redundancy') :
                categ_ids.append(emp.id)
            elif self.env.user.has_group('surgi_evaluation.all_permission_group_redundancy') :
                categ_ids.append(emp.id)

        return {
            'domain': {'employee_id': [('id', 'in', categ_ids)]}
        }

