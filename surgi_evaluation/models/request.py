from odoo import models, fields, api
class RequestRelegation(models.Model):
    _name = 'request.relegation'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    full_name = fields.Char(string="Full Name", required=False, )
    emp_image = fields.Binary(related='employee_id.image_1920')
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    section_id = fields.Many2one(comodel_name="hr.department", string="Section", related='employee_id.section_id')
    registration_number = fields.Char(string="Registration Number of the Employee",
                                      related='employee_id.registration_number')
    grade_id = fields.Many2one(comodel_name="grade.grade", string="Grade", )
    rank_id = fields.Many2one(comodel_name="rank.rank", string="Rank", )
    rang_id = fields.Many2one(comodel_name="rang.rang", string="Range", )

    new_field_ids = fields.Many2many(comodel_name="", relation="", column1="", column2="", string="", )

    human_resources_ids = fields.Many2many(comodel_name="custody.custody", string="Human Resources", )
    finance_ids = fields.Many2many(comodel_name="custody.custody",relation="finance", column1="finance1", column2="finance2", string="Finance", )
    administration_ids = fields.Many2many(comodel_name="custody.custody",relation="administration", column1="administration1", column2="administration2", string="Administration", )
    warehouse_ids = fields.Many2many(comodel_name="custody.custody",relation="warehouse", column1="warehouse1", column2="warehouse2", string="Warehouse", )
    purchasing_logistic_ids = fields.Many2many(comodel_name="custody.custody",relation="purchasing_logistic", column1="purchasing_logistic1", column2="purchasing_logistic2", string="Purchasing Logistic", )
    information_system_ids = fields.Many2many(comodel_name="custody.custody",relation="information_system", column1="information_system1", column2="information_system2", string="Information System", )
    scientific_office_ids = fields.Many2many(comodel_name="custody.custody",relation="scientific_office", column1="scientific_office1", column2="scientific_office2", string="Scientific Office", )
    tenders_ids = fields.Many2many(comodel_name="custody.custody",relation="tenders", column1="tenders1", column2="tenders2", string="Tenders", )
    collection_ids = fields.Many2many(comodel_name="custody.custody",relation="collection", column1="collection1", column2="collection2", string="Collection", )
    sales_ids = fields.Many2many(comodel_name="custody.custody",relation="sales", column1="sales1", column2="sales2", string="Sales", )
    maintenance_ids = fields.Many2many(comodel_name="custody.custody",relation="maintenance", column1="maintenance1", column2="maintenance2", string="Maintenance & after Sales", )
    legal_affair_ids = fields.Many2many(comodel_name="custody.custody",relation="legal", column1="legal1", column2="legal2", string="Legal Affair", )
    marketing_ids = fields.Many2many(comodel_name="custody.custody",relation="marketing", column1="marketing1", column2="marketing2", string="Marketing", )
    medical_devices_ids = fields.Many2many(comodel_name="custody.custody",relation="medical", column1="medical1", column2="medical2", string="Medical Devices", )
    direct_manager_ids = fields.Many2many(comodel_name="custody.custody",relation="direct_manager", column1="direct_manager1", column2="direct_manager2", string="Direct Manager", )



    @api.onchange('employee_id')
    def get_employee_grad(self):
        self.grade_id = self.employee_id.grade_id.id
        self.rank_id = self.employee_id.rank_id.id
        self.rang_id = self.employee_id.rang_id.id
