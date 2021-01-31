from datetime import date,datetime,time,timedelta
from odoo import api,_
from odoo import exceptions
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class surgi_outdoor_attendance(models.Model):
     _name = 'surgi.outdoor.attendance'
     _inherit = ['mail.thread']
     _order = 'ref'



     @api.constrains('op_start_datetime')
     def const_op_start_datetime(self):
         if self.op_start_datetime:
             today_date=datetime.now()
             op_start_datetime = datetime.strptime(str(self.op_start_datetime).split(".")[0], '%Y-%m-%d %H:%M:%S').date()
             today = datetime.strptime(str(today_date).split(".")[0], '%Y-%m-%d %H:%M:%S').date()

             if op_start_datetime <= today:
                 raise ValidationError(_('Not allowed Start DateTime'))


     def _get_currunt_loged_user(self):
         return self.env.user.id

     def cron_daily_plan(self):
         today_date = fields.Datetime().now()
         print("4$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

         time2 = "22:00:00"
         my_datetime = datetime.strptime(time2, "%H:%M:%S")
         for user in self.env['hr.employee'].search([('set_daily_plan','=',True)]):
             list_free = []

             for plan in self.env['surgi.outdoor.attendance'].search([]):
                 if plan.op_start_datetime:
                     op_start_datetime = datetime.strptime(str(plan.op_start_datetime).split(".")[0], '%Y-%m-%d %H:%M:%S').date()
                     today = datetime.strptime(str(today_date).split(".")[0], '%Y-%m-%d %H:%M:%S').date()+relativedelta(days=1)
                     if user.user_id==plan.employee_name and today==op_start_datetime:

                         if plan.employee_name.id not in list_free:
                            list_free.append(user.user_id.id)


             if today_date.time() <= my_datetime.time():
                 if user.user_id.id not in list_free or list_free == []:
                     self.env['surgi.outdoor.attendance'].sudo().create({'employee_name': user.user_id.id,
                                                                         'op_start_datetime': today_date+timedelta(days=1),
                                                                         'state_employee': 'free'})



     employee_name = fields.Many2one(comodel_name='res.users', string="Responsible", default=_get_currunt_loged_user,
                                   track_visibility='onchange')
     ref = fields.Char(string="Ref", related='employee_name.partner_id.ref', readonly=True)
     mobile = fields.Char(string="Mobile", related='employee_name.partner_id.mobile', readonly=True)
     sales_area = fields.Many2one('crm.team', string='Sales Channel', oldname='section_id',
                                   default=lambda self: self.env['crm.team'].search(
                                       ['|', ('user_id', '=', self.env.uid), ('member_ids', '=', self.env.uid)],
                                       limit=1))
     area_manager = fields.Many2one(comodel_name='res.users', string="Area Manager", related='sales_area.user_id',readonly=True)

     operation_id = fields.Many2one('operation.operation', string="Operation", track_visibility='onchange')
     operation_type = fields.Many2one('product.operation.type' ,string="Type",readonly=True,related='operation_id.operation_type')#related='operation_id.operation_type',
     hospital = fields.Many2one('res.partner', string="Hospital", readonly=True,related='operation_id.hospital_id')# related='operation_id.hospital_id',
     surgeon = fields.Many2one('res.partner', string="Surgeon", readonly=True,related='operation_id.surgeon_id')# related='operation_id.surgeon_id',
     op_start_datetime = fields.Datetime('Start DateTime',)#related='operation_id.start_datetime',

     state_employee = fields.Selection(string="State Employee", selection=[('operation', 'Operation'), ('mission', 'Mission'),('free','Free'),('not_set','Not Set')],)
     state_employee2 = fields.Selection(string="State Employee", selection=[('not_set','Not Set')],)
     is_set = fields.Boolean(string="",  )
     mission_description= fields.Text(string="description", required=False, )

     op_start_date = fields.Date(string="",compute='calculate_op_start_date',store=True )
     op_start_today = fields.Date(string="",compute='calculate_op_start_date',store=True)

     @api.depends('op_start_datetime')
     def calculate_op_start_date(self):

         self.op_start_date=False
         self.op_start_today=False

         for rec in self:
             if rec.op_start_datetime:
                op_start_date=datetime.strptime(str(rec.op_start_datetime).split(".")[0], '%Y-%m-%d %H:%M:%S').date()
                rec.op_start_date=op_start_date
                rec.op_start_today = op_start_date - relativedelta(days=1)
                print(op_start_date,rec.op_start_date,rec.op_start_today,'KKKKKKKKKKKKK')
             else:
                rec.op_start_date = False
                rec.op_start_today = False


     @api.onchange('state_employee2')
     def calculate_state_employee2(self):
         self.state_employee=self.state_employee2

     @api.onchange('operation_id','employee_name')
     def calculate_op_start_datetime(self):
        today_date = datetime.now()
        time2 = "22:00:00"
        my_datetime = datetime.strptime(time2, "%H:%M:%S")

        today = datetime.strptime(str(today_date).split(".")[0], '%Y-%m-%d %H:%M:%S').date()
        if today_date.time() > my_datetime.time():
            print("XXXXXXXXXXXXXXXXXXXXX")
            self.is_set = True
            self.op_start_datetime = self.operation_id.start_datetime
            self.op_start_datetime=today_date + timedelta(days=1)


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    set_daily_plan = fields.Boolean(string="Can Set Daily Plan",  )

    def button_payslip(self):
        return False
