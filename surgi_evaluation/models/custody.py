from odoo import models, fields, api
class CustodyCustody(models.Model):
    _name = 'custody.custody'
    _rec_name = 'name'

    name = fields.Char()
    department_ids = fields.Many2one(comodel_name="evaluation.department", string="Department", )
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employee", )
    type = fields.Selection(string="Department", selection=[
        ('direct_manager','Direct Manager'),
        ('hr', 'Human Resource'), ('finance', 'Finance'),
        ('administration', 'Administration'), ('warehouse', 'Warehouse'),
        ('purchasing_logistic', 'Purchasing Logistic'), ('information_system', 'Information System'),
        ('scientific_office', 'Scientific Office'), ('Tenders', 'Tenders'),
        ('collection', 'Collection'), ('sales', 'Sales'),
        ('maintenance_sales', 'Maintenance & After Sales'), ('legal', 'Legal Affair'),
        ('marketing', 'Marketing'), ('medical', 'Medical Device'),

    ], required=False, )