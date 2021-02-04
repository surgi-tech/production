from odoo import models, fields, api
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    hospital_id = fields.Many2one(comodel_name="res.partner", string="Hospital", )
    surgeon_id = fields.Many2one(comodel_name="res.partner", string="Surgeon", )
    patient_name = fields.Char(string="Patient Name", required=False, )
    sales_area_manager = fields.Many2one(comodel_name="res.users", string="Area Manager", )
    collection_rep = fields.Many2one(comodel_name="res.users", string="Collection Rep", )
    so_type = fields.Selection([('normal', 'Normal'),
                                ('operation', 'Operation'),
                                ('tender', 'Tender'),
                                ('supply_order', 'Supply Order'),
                                ], string='Sale Order Type', default="normal")
    suregon_code = fields.Char(string="Surgeon Code", required=False, )
    authority = fields.Selection([
        ('closed', 'Closed'),
        ('open', 'Open'),
        ('open_approval', 'Open with Approval')
    ], string='Authority Type')
    customer_category = fields.Selection([('taelimia','Educational Hospitals'),('private_uh','Private Universities Hospitals'),('public_uh','Public Universities Hospitals'),('military','Military Hospitals'),('insurance','Health Insurance Hospitals'),('muasasat','Almoasasat Aleilajia'),('private','Private Hospitals'),('moh','MOH'),('alhayyat','Alhayyat Hospitals'),('jihat_kharijia','Jihat Kharijia'),('alameenah','Al Ameenah Hospitals'),('individual','Individual'),('surgeon','surgeon'),('company','Private Company'),('pharmacy','Pharmacy'),('lab','Lab')])

    suregon_code_hospital = fields.Char(string="Hospital Surgeon Code", required=False, )
    authority_hospital = fields.Selection([
        ('closed', 'Closed'),
        ('open', 'Open'),
        ('open_approval', 'Open with Approval')
    ], string='Hospital Authority Type')
    customer_category_hospital = fields.Selection(
        [('taelimia', 'Educational Hospitals'), ('private_uh', 'Private Universities Hospitals'),
         ('public_uh', 'Public Universities Hospitals'), ('military', 'Military Hospitals'),
         ('insurance', 'Health Insurance Hospitals'), ('muasasat', 'Almoasasat Aleilajia'),
         ('private', 'Private Hospitals'), ('moh', 'MOH'), ('alhayyat', 'Alhayyat Hospitals'),
         ('jihat_kharijia', 'Jihat Kharijia'), ('alameenah', 'Al Ameenah Hospitals'), ('individual', 'Individual'),
         ('surgeon', 'surgeon'), ('company', 'Private Company'), ('pharmacy', 'Pharmacy'), ('lab', 'Lab')])

    ref = fields.Char(string="Ref", required=False, )
    sale_name = fields.Char(string="Sales Name", required=False, )
    delivery_name = fields.Char(string="Delivery Name", required=False, )
    customer_country = fields.Char(string="customer Country ", required=False, )
    customer_city = fields.Char(string="City", required=False, )


    sales_person_id = fields.Many2one(comodel_name="res.users", string="Salesperson", required=False, )
    team_id = fields.Many2one(comodel_name="crm.team", string="Sales Team", required=False, )
    op_type = fields.Selection([
        ('private', 'Private'),
        ('tender', 'Waiting List'),
        ('supply_order', 'Supply Order'),
    ], string='Type',)

class SalesOrderInherit(models.Model):
    _inherit = 'sale.order'
    op_type = fields.Selection([
        ('private', 'Private'),
        ('tender', 'Waiting List'),
        ('supply_order', 'Supply Order'),
    ], string='Type', related='operation_id.op_type')


    def _prepare_invoice(self):
        res=super(SalesOrderInherit, self)._prepare_invoice()
        print(res,'HHHHHHHHHHHHHHHHHHHHHH')


        res['hospital_id']=self.hospital_id.id
        res['surgeon_id']=self.surgeon_id.id
        res['patient_name']=self.patient_name
        res['collection_rep']=self.collection_rep
        res['sales_area_manager']=self.sales_area_manager.id
        res['patient_name']=self.patient_name
        res['sales_person_id']=self.user_id.id
        res['team_id']=self.team_id.id
        res['op_type']=self.op_type

        res['suregon_code']=self.surgeon_id.suregon_code
        res['authority']=self.surgeon_id.authority
        res['customer_category']=self.surgeon_id.customer_category
        res['suregon_code_hospital']=self.hospital_id.suregon_code
        res['authority_hospital']=self.hospital_id.authority
        res['customer_category_hospital']=self.hospital_id.customer_category
        res['ref']=self.hospital_id.ref
        res['sale_name']=self.name
        res['delivery_name']=self.picking_ids.name
        res['customer_country']=self.partner_id.country_id.name
        res['customer_city']=self.partner_id.state_id.name

        return res

        # invoice_vals = super()._prepare_invoice()
        # invoice_vals['invoice_incoterm_id'] = self.incoterm_id.id
        # return invoice_vals