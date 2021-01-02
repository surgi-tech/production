from datetime import datetime
from odoo import api
from odoo import fields
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import pytz
#from odoo.tools import timedelta
from datetime import timedelta
class surgitech_tender_hospital_sectors(models.Model):
    _name = 'hospital.sectors'

    tender_id = fields.Integer('Tender Id')
    name = fields.Char('Name')

class surgitech_tender_hospital_categories(models.Model):
    _name = 'hospital.categories'

    tender_id = fields.Integer('Tender Id')
    name = fields.Char('Name')
    sector_id = fields.Many2one('hospital.sectors', 'Sector', ondelete="set null")

class surgitech_tender_operation_type_parent(models.Model):
    _name = 'product.operation.type.parent'

    tender_id = fields.Integer('Tender Id')
    name = fields.Char('Name')

class surgitech_tender_res_partner(models.Model):
    _inherit = 'res.partner'

    tender_id = fields.Integer('Tender Id')
    integration = fields.Boolean(default=False)
    tender_sector_id = fields.Many2one('hospital.sectors', string='Tender Sector')
    tender_category_id = fields.Many2one('hospital.categories', string='Tender Category')

#    @api.model
#    def create(self, vals):
#        print '--------------------------------------'
#        print str(vals)
#        if 'integration' in vals and vals['integration'] == 'True':
#            patient = self.env['res.partner'].search([('national_id', '=', vals['national_id'])])
#            if(patient):
#                patient.write(vals)
#                return patient
#        return super(surgitech_tender_res_partner, self).create(vals)

class surgitech_tender_operation_type(models.Model):
    _inherit = 'product.operation.type'

    tender_id = fields.Integer('Tender Id')
    parent_category_id = fields.Many2one('product.operation.type.parent', 'Parent Category', ondelete="set null")

class surgitech_tender_operation_product(models.Model):
    _inherit = 'product.product'
    #product_tender_rel=fields.many2many("operation.operation","tender_component_ids")
    tender_id = fields.Integer('Tender Id')

class surgitech_tender_operation_operation(models.Model):
    _inherit = 'operation.operation'

   # @api.one
    def _can_cancel(self):
        if self.create_uid.id == self.env.uid or self._check_employee_manager() == True or self.env.user.has_group("surgitech_operation.group_warehouse_coordinator"):
            self.can_cancel = True
        else:
            self.can_cancel = False

  #  @api.one
    def _check_employee_manager(self):
        for employee in self.env['hr.employee'].search([('user_id', '=', self.create_uid.id)]):
            if employee.parent_id and employee.parent_id.user_id and employee.parent_id.user_id.id == self.env.uid:
                return True
        return False

   # @api.one
    def _get_is_coordinator(self):
        return self.env.user.has_group("surgitech_operation.group_warehouse_coordinator")

    tender_id = fields.Integer('Tender Id')
    integration = fields.Boolean(default=False)
    sector_id = fields.Many2one('hospital.sectors', 'Tender Sector', ondelete="set null")
    category_id = fields.Many2one('hospital.categories', 'Tender Category', ondelete="set null")
    hospital_additional_notes = fields.Text(string="Hospital Notes")
    tender_component_ids = fields.Many2many('product.product', "tender_product_rel",string="Components")
    can_cancel = fields.Boolean(compute="_can_cancel", default=False)
    is_coordinator = fields.Boolean(compute="_get_is_coordinator")
    start = fields.Text("Start")
    stop = fields.Text("Stop")

    @api.model
    def create(self, vals):
        print( '--------------------------------------------------------')
        print (vals)
        if 'integration' in vals and vals['integration'] == 'True':
            vals['hospital_id'] = self.env['res.partner'].search([('tender_id', '=', vals['hospital_id']), ('is_hospital', '=', True)]).id
            vals['surgeon_id'] = self.env['res.partner'].search([('tender_id', '=', vals['surgeon_id']), ('is_surgeon', '=', True)]).id
            vals['sector_id'] = self.env['hospital.sectors'].search([('tender_id', '=', vals['sector_id'])]).id
            vals['category_id'] = self.env['hospital.categories'].search([('tender_id', '=', vals['category_id'])]).id
            vals['operation_type'] = self.env['product.operation.type'].search([('tender_id', '=', vals['operation_type'])]).id
            vals['patient_id'] = self.env['res.partner'].search([('tender_id', '=', vals['patient_id']), ('is_patient', '=', True)])[0].id
            vals['component_ids'] = [(6, 0, [x.id for x in self.env['product.product'].search([('tender_id', 'in', vals['component_ids'])])])]
            vals['tender_component_ids'] = vals['component_ids']
        if 'start' not in vals:
            start = datetime.strptime(vals['start_datetime'], DEFAULT_SERVER_DATETIME_FORMAT).replace(second=0, microsecond=0)
            vals['start'] = str((start + timedelta(hours=3)))
            vals['stop'] = str((start + timedelta(hours=3)))
            vals['start_datetime'] = datetime.strptime(vals['start_datetime'], DEFAULT_SERVER_DATETIME_FORMAT)
        print (vals)
        return super(surgitech_tender_operation_operation, self).create(vals)

    #@api.multi
    def write(self, vals):
        print ('--------------------------------------')
        print (vals)
        for rec in self:
            if 'integration' not in vals and rec.tender_id > 0 and 'tender_component_ids' in vals:
                vals['component_ids'] = vals['tender_component_ids']
            if 'integration' in vals and vals['integration'] == 'True':
                vals['integration'] = False
                if 'hospital_id' in vals:
                    vals['hospital_id'] = self.env['res.partner'].search([('tender_id', '=', vals['hospital_id']), ('is_hospital', '=', True)]).id
                    vals['surgeon_id'] = self.env['res.partner'].search([('tender_id', '=', vals['surgeon_id']), ('is_surgeon', '=', True)]).id
                    vals['sector_id'] = self.env['hospital.sectors'].search([('tender_id', '=', vals['sector_id'])]).id
                    vals['category_id'] = self.env['hospital.categories'].search([('tender_id', '=', vals['category_id'])]).id
                    vals['operation_type'] = self.env['product.operation.type'].search([('tender_id', '=', vals['operation_type'])]).id
                    vals['component_ids'] = [(6, 0, [x.id for x in self.env['product.product'].search([('tender_id', 'in', vals['component_ids'])])])]
                    vals['tender_component_ids'] = vals['component_ids']
                    if 'start' not in vals:
                        start = datetime.strptime(vals['start_datetime'], DEFAULT_SERVER_DATETIME_FORMAT).replace(second=0, microsecond=0)
                        vals['start'] = str((start + timedelta(hours=3)))
                        vals['stop'] = str((start + timedelta(hours=3)))
                        vals['start_datetime'] = datetime.strptime(vals['start_datetime'], DEFAULT_SERVER_DATETIME_FORMAT)
                    if 'state' in vals and vals['state'] == 'cancel':
                        reason_id = self.env['operation.cancel.reason'].create({
                                                                               'name': vals['reason'],
                                                                               })
                        vals['reason'] = reason_id.id
                    return rec.write(vals)
                if 'state' in vals and vals['state'] == 'cancel':
                    reason_id = self.env['operation.cancel.reason'].create({
                                                                           'name': vals['reason'],
                                                                           })
                    print ('-----------------------------------------------------')
                    print (reason_id.id)
                    return rec.write({
                                     'reason': reason_id.id,
                                     'description': vals['reason'],
                                     'state':'cancel'
                                     })
            return super(surgitech_tender_operation_operation, self).write(vals)

    def sync_tender_odoo(args):
        for rec in args:
            print (rec)
            break
