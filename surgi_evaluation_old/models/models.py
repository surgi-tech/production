from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
from datetime import datetime, timedelta, date
import time
from pytz import timezone


class NewModule(models.Model):
    _inherit = 'hr.employee'

    evaluation_method = fields.Selection(string="Evaluation Method", selection=[('dm', 'Direct Manager'), ('average', 'Average'),('pm','Parent Manager') ], required=False, )

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     args = args or []
    #     domain_name = ['|', ('name', 'ilike', name), ('pin', 'ilike', name)]
    #     recs = self.search(domain_name + args, limit=limit)
    #     return recs.name_get()


class NewModule(models.Model):
    _inherit = 'hr.job'

    kpi_ids = fields.One2many(comodel_name="kpi.kpi", inverse_name="interval_employee", )

    # @api.constrains('kpi_ids')
    # def get_hours_custom(self):
    #     total = 0.0
    #     for rec in self.kpi_ids:
    #         print ('************************************************')
    #         total += rec.weight
    #     print ('ttttttttttttttttt', total)
    #     if total > 1:
    #         raise UserError(_('weight % Must be in 100%'))


class KPIEMPLOYEE(models.Model):
    _name = 'kpi.kpi'

    name = fields.Char(string="KPI", required=False, )
    weight = fields.Float(string="weight %", required=False, )
    active_kpi = fields.Boolean('Active', default=False, )

    kra_kpi = fields.Char(string="KRA", required=False, )

    interval_employee = fields.Many2one(comodel_name="hr.job", string="Job Postion")

    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('review','Reviewing'),
        ('waiting', 'Waiting Activation'),
        ('activated', 'Activated')], string='Status',
        copy=False, default='draft', index=True, readonly=True,
        help="* New: New KPI"
             "* Waiting Activation: KPI Waiting HR Activation"
             "* Activated: KPI Activated"
             "* Cancelled: KPI Cancelled")

    def rest_kpi(self):
        self.active_kpi = False
        self.state = 'draft'

    def submit_kpi(self):
        self.state = 'waiting'

    def review_kpi(self):
        self.active_kpi = False
        self.state = 'review'

    def activate_kpi(self):
        self.active_kpi = True
        self.state = 'activated'

    def cancel_kpi(self):
        self.active_kpi = False
        self.state = 'cancel'

    @api.onchange('name', 'weight', 'kra_kpi', 'interval_employee')
    def _onchange_active_kpi(self):
        if self.active_kpi:
            self.active_kpi = False
            self.state = 'draft'

    # @api.onchange('name')
    # def tags_get(self):
    #     categ_ids = []
    #     employee_rec = self.env['hr.jop'].search([])
    #
    #     for emp in employee_rec:
    #         if emp == self.env.user:
    #             print ('1111111111111111111111111111111111111111111111111')
    #             categ_ids.append(emp.id)
    #     print ('+++++++++++++++++', categ_ids)
    #     return {
    #         'domain': {'interval_employee': [('id', 'in', categ_ids)]}
    #     }

    # @api.constrains('weight')
    # def get_kpi_employee(self):
    #     total = 0.0
    #     kpi_rec = self.env['kpi.kpi'].search([])
    #     for rec in kpi_rec:
    #         total += rec.weight
    #     print ('++++++++++++++++', total)
    #     if total > 1:
    #         raise UserError(_('total weight for certain Employee  must = 100%'))

    # @api.onchange('active_kpi')
    # def kpi_manger_check_active(self):
    #     manger_hr = self.env.user.has_group('surgi_evaluation.kpi_manger_groups_employee')
    #
    #     if not manger_hr:
    #         if self.name or self.weight or self.interval_employee:
    #             self.active_kpi = False

    ### Notice (1) ####
    # 1- weight Field need to be percentage filed
    # 3- view located in menu called ( KPI ) under Evaluation Menu for members in (KPI Manager Group)
    # 4- KPI Manager Group) see or edit kpi for his subordinates only
    # 5- KPI Manager Group) can make new Kpi for his subordinates only by limit employee in interval_employee on his subordinates only
    # 6- total weight Field for certain (interval_employee)  must = 100% (api.onchange for interval_employee) and with save
    # 7- any changes in KPI change active field to False (if not hr group )
    # 8- view for hr team as it's in employee form but add active field on it , total for active record only and must be 100%
    ### Notice (1) end ###


class NewModule(models.Model):
    _name = 'competencies.ratio'

    ### Notice (2) start ###
    core_ratio = fields.Float(string="Core Competencies Ratio", required=False, tracking=True, )
    function_ratio = fields.Float(string="Function Competencies Ratio", required=False,
                                  tracking=True, )  # defult value = 1
    kpi_ratio = fields.Float(string="KPI Competencies Ratio", required=False, tracking=True, )  # defult value = 1

    ### Notice (2) ####
    # 1- above Field need to be percentage filed
    # 3- view located in menu called ( Competencies Ratios ) under configuration menu under Evaluation Menu for HR team only
    ### Notice (2) end ###


class EvaluationEvaluation(models.Model):
    _name = 'evaluation.evaluation'

    # Notice every manager see evaluations for his subordinate only ##
    name = fields.Char(string="Evaluation", required=True, )
    # Notice we can enter registration_number or employee_id to get employee info ##
    # registration_number = fields.Char('Registration Number of the Employee',related='employee_id.registration_number', copy=False)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    department_id = fields.Many2one(comodel_name="hr.department", related='employee_id.department_id', readonly=True,
                                    store=True)
    employee_parent_id = fields.Many2one(comodel_name="hr.employee", related='employee_id.parent_id', readonly=True,
                                         store=True)
    jop_ids = fields.Many2one(comodel_name="hr.job", string="Job Postion", related='employee_id.job_id')

    # Notice Manager cant see inactive evaluation #
    active_evaluation = fields.Boolean('Active', default=True, tracking=True, )

    # Notice Manager cant edit or submit or change evaluation out of the below dates & duration #
    date_start = fields.Date('Start Date', required=True, )
    date_end = fields.Date('End Date')
    duration = fields.Float('Duration', store=True, readonly=True)  # compute='_compute_duration',
    check_read = fields.Boolean(string="Publish for Employee", default=False)
    check_esa = fields.Boolean(string="Employee Self Assessment Evaluated", default=False)
    check_direct_manager = fields.Boolean(string="Direct Manager Evaluated", default=False)
    check_indirect_manager = fields.Boolean(string="IN-Direct Manager Evaluated", default=False)

    is_evalualtion = fields.Boolean(string="Get", defaut=False)

    # Notice get all question in core.competencies which active only # HR ONLY
    core_competencies = fields.One2many(comodel_name="core2.competencies2", inverse_name="interval_core", )
    # Notice get all question in function.competencies which active only #  HR ONLY
    function_comp = fields.One2many(comodel_name="function2.competencies2", inverse_name="interval_function", )
    # Notice get all question in kpi.competencies for the mention employee which active only #
    employee_kpi = fields.One2many(comodel_name="kpi.competencies", inverse_name="interval_kpi", )

    total_competencies = fields.Float(string="Total Core", compute='get_total_core_competencies', store=True)
    total_function_comp = fields.Float(string="Total Function", required=False, compute='get_total_function_comp',
                                       store=True)
    total_employee_kpi = fields.Float(string="Total KPI", required=False, compute='get_total_total_employee_kpi',
                                      store=True)
    total_totals = fields.Float(string="Total", compute='get_total_total', store=True)
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('esa', 'Self Assessment'),('direct_manager', 'Direct Manager'),('indirect_manager', 'IN-Direct Manager'),('done', 'Done'), ], required=False, )

    check_eval = fields.Boolean(string="Check Evaluation", default=False)

    accrual_date = fields.Date('Accrual Date', required=False)

    # evaluate_by_parent = fields.Boolean(string="Evaluate By Parent Manager", )
    # evaluate_by_parent_indirect = fields.Boolean(string="Evaluate By Parent Indirect Manager", )
    #
    # parent_managager = fields.Many2one(comodel_name="hr.employee", related='employee_parent_id.parent_id',
    #                                    string="Parent Manager", store=True)

    indirect_manager_id = fields.Many2one(comodel_name="hr.employee",related='employee_id.in_direct_parent_id' ,string="Indirect Manager",store=True)

    state_quarter = fields.Selection(string="Quarter",
                                     selection=[('q1', 'Q1'), ('q2', 'Q2'), ('q3', 'Q3'), ('q4', 'Q4')])#, readonly=True
    month = fields.Selection([('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'),
                              ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'),
                              ('September', 'September'), ('October', 'October'), ('November', 'November'),
                              ('December', 'December'), ], string='Month')#, readonly=True

    evaluation_method = fields.Selection(string="Evaluation Method", selection=[('dm', 'Direct Manager'), ('average', 'Average'),('pm','Parent Manager') ], required=False, )

    @api.onchange('employee_id')
    def _compute_evaluation_method(self):
        self.evaluation_method=self.employee_id.evaluation_method

    # is_xx = fields.Boolean(string="", compute='_compute_indirect_manager' )

    # @api.depends('evaluate_by_parent_indirect')
    # def _compute_indirect_manager(self):
    #     print("sssssssssssssssssssssssssssssssssssssssssssssss")
    #     self.is_xx=True
    #     # if self.evaluate_by_parent_indirect==True:
    #     #     print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
    #     #     for rec in self.core_competencies:
    #     #         rec.is_indirect=True

    @api.onchange('date_start')
    def _compute_month_quarter(self):
        print("111111111111111111111")
        if self.date_start:
            month_name = str(datetime.strptime(str(self.date_start), '%Y-%m-%d').date().strftime('%B'))
            print('222222222222222222', month_name)
            self.month = month_name
            if month_name in ['January', 'February', 'March']:
                self.state_quarter = 'q1'
            if month_name in ['April', 'May', 'June']:
                self.state_quarter = 'q2'
            if month_name in ['July', 'August', 'September']:
                self.state_quarter = 'q3'
            if month_name in ['October', 'November', 'December']:
                self.state_quarter = 'q4'

    #######################################

    def write(self, values):

        # values['is_evalualtion'] = True
        return super(EvaluationEvaluation, self).write(values)

    @api.onchange('name')
    def get_lines_cor(self):

        lines = [(5, 0, 0), ]
        lines2 = [(5, 0, 0), ]

        for rec in self.env['core.competencies'].search([]):

            if rec.active_core == True:
                lines.append((0, 0, {
                    'name': rec.name,
                    'kpi_weight': rec.kpi_weight,
                    'state_result': rec.state_result,
                    # 'state_result': "expectation",
                }))

        for rec in self.env['function.competencies'].search([]):
            print('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
            if rec.active_function == True:
                print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
                lines2.append((0, 0, {
                    'name': rec.name,
                    'kpi_weight': rec.kpi_weight,
                    'state_result': rec.state_result,
                    # 'state_result': "expectation",
                }))
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<', lines2)
        self.update({'core_competencies': lines, 'function_comp': lines2})
        # self.update({'function_comp': lines2})

        # list_lines=[]
        # for rec in self.env['core.competencies'].search([('active_core','=','True')]):
        #     list_lines.append(rec.id)
        # print (list_lines,'----------------------------------')
        # self.write({'core_competencies': list_lines })
        #
        # list_lines2 = []
        # for rec in self.env['function.competencies'].search([('active_function', '=', 'True')]):
        #     list_lines2.append(rec.id)
        # print (list_lines, '----------------------------------')
        # self.write({'function_comp': list_lines2})
        #

    def submit_core(self):
        total = 0.0
        # total2 = 0.0
        # total3 = 0.0
        for rec in self.function_comp:
            total += rec.kpi_weight
        if total != 1:
            raise UserError(_('KPI Function weight  % Must be in 100%'))

        # for rec in self.core_competencies:
        #     total2 += rec.kpi_weight
        # if total2 != 1:
        #     raise UserError(_('KPI Competencies weight % Must be in 100%'))

        # for rec in self.employee_kpi:
        #     total3 += rec.kpi_weight
        # if total3 != 1:
        #     raise UserError(_('KPI Employee weight % Must be in 100%'))

        else:
            self.state = 'done'
            self.check_read = True

    def submit_esa(self):
        self.state = 'esa'
        self.check_esa = True

    def submit_direct_manager(self):
        self.state = 'direct_manager'
        self.check_direct_manager = True

    def submit_indirect_manager(self):
        self.state = 'indirect_manager'
        self.check_indirect_manager = True

    @api.constrains('function_comp')  # ,'core_competencies','employee_kpi'
    def submit_core_weight(self):
        total = 0.0
        # total2=0.0
        # total3=0.0
        for rec in self.function_comp:
            total += rec.kpi_weight
        if total != 1:
            raise UserError(_('KPI Function weight  % Must be in 100%'))

        # for rec in self.core_competencies:
        #     total2 += rec.kpi_weight
        # if total2 != 1:
        #     raise UserError(_('KPI Competencies weight % Must be in 100%'))
        #
        # for rec in self.employee_kpi:
        #     total3 += rec.kpi_weight
        # if total3 != 1:
        #     raise UserError(_('KPI Employee weight % Must be in 100%'))

    ####################################
    @api.onchange('name')
    def tags_get(self):
        categ_ids = []
        employee_rec = self.env['hr.employee'].search([])

        for emp in employee_rec:
            if emp.parent_id.user_id == self.env.user:
                print('1111111111111111111111111111111111111111111111111')

                categ_ids.append(emp.id)
        print('+++++++++++++++++', categ_ids)
        return {
            'domain': {'employee_id': [('id', 'in', categ_ids)]}
        }

    #######################################################
    @api.onchange('date_start', 'date_end')
    def _compute_duration_days(self):

        if self.date_start and self.date_end:
            date_start = datetime.strptime(str(self.date_start), "%Y-%m-%d").date()
            date_end = datetime.strptime(str(self.date_end), "%Y-%m-%d").date()
            print(date_start, date_end, '+++++++++++++++')
            self.duration = float(str((date_end - date_start).days))

    def _compute_duration(self):

        today_dat = date.today()
        # print ('salah000000000000000000000000000000000000000000000salah', today_dat)

        for rec in self.search([]):
            if rec.date_end:
                date_end = datetime.strptime(str(rec.date_end), "%Y-%m-%d").date()
                today_date = datetime.strptime(str(today_dat), "%Y-%m-%d").date()
                print('+++++++++++++++++++++++++++++', date_end)
                print('+++++++++++++++++++++++++++++', today_date)

            if today_date > date_end:
                print('+++++++++++++++++++++++++++++')
                rec.check_read = True

    @api.depends('total_competencies', 'total_function_comp', 'total_employee_kpi', 'total_totals', 'total_totals')
    def get_total_total(self):
        ratio = self.env['competencies.ratio'].search([], order='id desc', limit=1)
        for rec in self:
            # rec.total_totals = (rec.total_competencies + rec.total_function_comp + rec.total_employee_kpi) / 3
            # Notice equation we need
            rec.total_totals = ((rec.total_competencies * ratio.core_ratio) + (
                        rec.total_function_comp * ratio.function_ratio) + (rec.total_employee_kpi * ratio.kpi_ratio))

    @api.depends('core_competencies', 'total_competencies')
    def get_total_core_competencies(self):
        total = 0.0
        for rec in self.core_competencies:
            total += rec.score
        self.total_competencies = total

    @api.depends('function_comp', 'total_function_comp')
    def get_total_function_comp(self):
        total = 0.0
        for rec in self.function_comp:
            total += rec.score
        self.total_function_comp = total

    @api.depends('employee_kpi', 'total_employee_kpi')
    def get_total_total_employee_kpi(self):
        total = 0.0
        for rec in self.employee_kpi:
            total += rec.score
        self.total_employee_kpi = total

    # @api.depends('totalcore_comp','total_totalcore_comp')
    # def get_total_totalcore_comp(self):
    #    total = 0.0
    #        for rec in self.totalcore_comp:
    #            total += rec.score
    #        self.total_totalcore_comp = total

    #    @api.depends('employee_kpi','total_employee_kpi')
    #    def get_totaltotal_employee_kpi(self):
    #        total = 0.0
    #        for rec in self.employee_kpi:
    #            total += rec.score
    #        self.total_employee_kpi = total

    @api.onchange('employee_id', 'jop_ids')
    def total_lines_employee_id(self):
        print('111111111111111111111111111')
        lines = [(5, 0, 0), ]
        if self.jop_ids.kpi_ids:
            for rec in self.jop_ids.kpi_ids:
                # lines.append(rec.id)
                if rec.active_kpi == True:
                    lines.append((0, 0, {
                        'name': rec.name,
                        'kpi_weight': rec.weight,
                        'kra_kpi': rec.kra_kpi,
                        # 'state_result': "expectation",
                    }))
            print('------------------------------------', lines)
        else:
            lines = [(5, 0, 0), ]
        self.update({'employee_kpi': lines})

        # self.update({'employee_kpi': lines,})

        # self.update({self.employee_kpi: self.employee_id.kpi_ids.id, })

    # @api.onchange('employee_id')
    # def employee_kpi(self):
    #     print ('11111111111111111')
    # for rec in self.employee_id.kpi_ids:
    #     rec.employee_kpi==rec.
    # self.update({'employee_kpi': self.employee_id.kpi_ids.id,})

    # @api.constrains('function_comp')
    # def get_function_comp(self):
    #     x = 0
    #     total = 0.0
    #     total2 = 0.0
    #     for rec in self.function_comp:
    #         total += rec.percentage
    #         total2 += rec.kpi_weight
    #         if rec.kpi_weight > 0:
    #             x += 1
    #         print ('xxxxxxxxxxxxxxxx', x)
    #         if x == 3:
    #             print ('2222222222222222222222', x)
    #             raise UserError(_('يلزم الاجابة على سؤلين فقط لا غير'))
    #         # if total != 100:
    #         #    raise UserError(_('percentage % Must be in 100%'))
    #
    #         # if total2 >= 100:
    #         #    raise UserError(_('KPI weight % Must be in 100%'))

    # @api.constrains('core_competencies')
    # def get_hours_custom(self):
    #     print ('+++++++++++++++++++++++++++++++++++')
    #     total = 0.0
    #     total2 = 0.0
    #     for rec in self.core_competencies:
    #         total += rec.percentage
    #         total2 += rec.kpi_weight
    #     print ('ttttttttttttttttt', total)
    # if total != 100:
    #    raise UserError(_('percentage % Must be in 100%'))

    # if total2 >= 100:
    #    raise UserError(_('KPI weight % Must be in 100%'))

    # @api.model
    # def default_get(self, fields):
    #     res = super(SurveySurvey, self).default_get(fields)
    #     print ("depends------------------------------------------------------------------------")
    #     manager_rec = [(5, 0, 0), ]
    #     manager_rec_total = [(5, 0, 0), ]
    #     # if not self.managers_opinions:
    #     manager_rec.append((0, 0, {
    #         'name': "يفهم ويتعلم من الآخرون‬‬",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #
    #     manager_rec.append((0, 0, {
    #         'name': "يطور الأفكار الجديدة التي توفر حلولا لجميع أنواع التحديات في مكان العمل.‬‬",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #     manager_rec.append((0, 0, {
    #         'name': "يلتزم بجميع قوانين وأنظمه والمعايير الخاصة بالعمل.‬‬",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #     manager_rec.append((0, 0, {
    #         'name': "لايحتاج لساعات عمل زائده عن وقت العمل للانتهاء من المهام الموكله له‬‬",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #     manager_rec.append((0, 0, {
    #         'name': "لديه روح التعاون مع الاخرين‬‬",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #     ####################################3
    #     manager_rec_total.append((0, 0, {
    #         'name': "يحل التحديات الصعبة أو المعقدة.",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #     manager_rec_total.append((0, 0, {
    #         'name': " يتحمل المسؤولية الشخصية عن جوده العمل وحسن توقيته، ويحقق النتائج مع القليل من الرقابة",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #
    #     manager_rec_total.append((0, 0, {
    #         'name': " يتكيف مع احتياجات العمل المتغيرة ، والظروف ، ومسؤوليات العمل.",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #
    #     manager_rec_total.append((0, 0, {
    #         'name': " أداره الوقت والأولويات والموارد الخاصة لتحقيق الأهداف",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #
    #     manager_rec_total.append((0, 0, {
    #         'name': " يعطي الاخرين طاقه ايجابيه ودفعه للعمل",
    #         'kpi_weight': 20,
    #         'state_result': "expectation",
    #     }))
    #
    #     res.update({'core_competencies': manager_rec, 'function_comp': manager_rec_total})
    #     # res.update({'function_comp': manager_rec_total})
    #     return res


class NewModule(models.Model):
    _name = 'core.competencies'
    _rec_name = 'name'

    name = fields.Char(string='Core')  # , groups="hr.group_hr_user"
    percentage = fields.Float(string="Final %", required=False, )
    kpi_weight = fields.Float(string="Weight", required=False, )
    state_result = fields.Selection(string="Result", selection=[('expectation', 'Rank of Expectation'),
                                                                ('improvement', 'Need To Improvement'),
                                                                ('meet', 'Meet'), ('exceed', 'Exceed'),
                                                                ('fail', 'Fail'), ], required=False)
    score = fields.Float(string="Score", required=False, compute='get_score', readonly=True,)
    active_core = fields.Boolean('Active', default=True,)
    employee_self_assessment = fields.Float(string="Employee Self Assessment", required=False, )
    direct_manager = fields.Float(string="Direct Manager", required=False, )
    in_direct_manager = fields.Float(string="In Direct Manager", required=False, )

    # interval_core22 = fields.Many2one(comodel_name="evaluation.evaluation")

    @api.depends('percentage', 'kpi_weight')
    def get_score(self):
        for rec in self:
            rec.score = (rec.percentage * rec.kpi_weight)

    # @api.constrains('kpi_weight')
    # def get_kpi_employee(self):
    #     total = 0.0
    #     kpi_rec = self.env['core.competencies'].search([])
    #     for rec in kpi_rec:
    #         total += rec.kpi_weight
    #     print ('++++++++++++++++', total)
    #     if total > 1:
    #         raise UserError(_('total weight for certain Employee  must = 100%'))


class NewModule(models.Model):
    _name = 'core2.competencies2'
    _rec_name = 'name'

    name = fields.Char(string='Core')  # , groups="hr.group_hr_user"
    percentage = fields.Float(string="Final %", required=False, )
    kpi_weight = fields.Float(string="KPI weight", required=False, )
    state_result = fields.Selection(string="Result", selection=[('expectation', 'Rank of Expectation'),
                                                                ('improvement', 'Need To Improvement'),
                                                                ('meet', 'Meet'), ('exceed', 'Exceed'),
                                                                ('fail', 'Fail'), ], required=False, )
    score = fields.Float(string="Score", required=False, compute='get_score', readonly=True, )
    active_core = fields.Boolean('Active', default=True, )
    employee_self_assessment = fields.Float(string="Employee Self Assessment", required=False, )
    direct_manager = fields.Float(string="Direct Manager", required=False, )
    in_direct_manager = fields.Float(string="In Direct Manager", required=False, )

    interval_core = fields.Many2one(comodel_name="evaluation.evaluation")
    # evaluation_method = fields.Selection(string="Evaluation Method", selection=[('dm', 'Direct Manager'), ('average', 'Average'),('pm','Parent Manager') ],related='interval_core.evaluation_method' )

    @api.onchange('direct_manager','in_direct_manager','interval_core')
    def get_final_total(self):
        print("ddddddddddddddddddddddddd",self.interval_core._origin)
        if self.interval_core.evaluation_method=='dm':
            self.percentage=self.direct_manager
        if self.interval_core.evaluation_method == 'average':
            self.percentage = (self.direct_manager+self.in_direct_manager)/2
        if self.interval_core.evaluation_method == 'pm':
            self.percentage = 0


    @api.depends('percentage', 'kpi_weight')
    def get_score(self):
        for rec in self:
            rec.score = (rec.percentage * rec.kpi_weight)


###########################################################################################################

class NewModule(models.Model):
    _name = 'function.competencies'
    _rec_name = 'name'

    name = fields.Char(string='Function')  # , groups="hr.group_hr_user"
    percentage = fields.Float(string="Final %", required=False, )
    kpi_weight = fields.Float(string="Weight", required=False, )
    state_result = fields.Selection(string="Result", selection=[('expectation', 'Rank of Expectation'),
                                                                ('improvement', 'Need To Improvement'),
                                                                ('meet', 'Meet'), ('exceed', 'Exceed'),
                                                                ('fail', 'Fail'), ], required=False)#,groups="hr.group_hr_user"
    score = fields.Float(string="Score", required=False, compute='get_score', readonly=True)
    active_function = fields.Boolean('Active', default=True)#, groups="hr.group_hr_user"
    employee_self_assessment = fields.Float(string="Employee Self Assessment", required=False, )
    direct_manager = fields.Float(string="Direct Manager", required=False, )
    in_direct_manager = fields.Float(string="In Direct Manager", required=False, )

    # interval_function = fields.Many2one(comodel_name="evaluation.evaluation")

    @api.depends('percentage', 'kpi_weight')
    def get_score(self):
        for rec in self:
            rec.score = (rec.percentage * rec.kpi_weight)

    # @api.constrains('kpi_weight')
    # def get_kpi_employee(self):
    #     total = 0.0
    #     kpi_rec = self.env['function.competencies'].search([])
    #     for rec in kpi_rec:
    #         total += rec.kpi_weight
    #     print ('++++++++++++++++', total)
    #     if total > 1:
    #         raise UserError(_('total weight for certain Employee  must = 100%'))


class NewModule(models.Model):
    _name = 'function2.competencies2'
    _rec_name = 'name'

    name = fields.Char(string='Questions')  # , groups="hr.group_hr_user"
    percentage = fields.Float(string="Final %", required=False, )
    kpi_weight = fields.Float(string="KPI weight", required=False, )
    state_result = fields.Selection(string="Result", selection=[('expectation', 'Rank of Expectation'),
                                                                ('improvement', 'Need To Improvement'),
                                                                ('meet', 'Meet'), ('exceed', 'Exceed'),
                                                                ('fail', 'Fail'), ])
    score = fields.Float(string="Score", required=False, compute='get_score', readonly=True, )
    active_function = fields.Boolean('Active', default=True)
    employee_self_assessment = fields.Float(string="Employee Self Assessment", required=False, )
    direct_manager = fields.Float(string="Direct Manager", required=False, )
    in_direct_manager = fields.Float(string="In Direct Manager", required=False, )

    interval_function = fields.Many2one(comodel_name="evaluation.evaluation")

    @api.onchange('direct_manager', 'in_direct_manager', 'interval_function')
    def get_final_total(self):
        if self.interval_function.evaluation_method == 'dm':
            self.percentage = self.direct_manager
        if self.interval_function.evaluation_method == 'average':
            self.percentage = (self.direct_manager + self.in_direct_manager) / 2
        if self.interval_function.evaluation_method == 'pm':
            self.percentage = 0


    @api.depends('percentage', 'kpi_weight')
    def get_score(self):
        for rec in self:
            rec.score = (rec.percentage * rec.kpi_weight)


##########################################################################3
class NewModule(models.Model):
    _name = 'kpi.competencies'
    _rec_name = 'name'

    name = fields.Char(string='KPI', )
    percentage = fields.Float(string="Final %", required=False, )
    kpi_weight = fields.Float(string="Weight", )
    state_result = fields.Selection(string="Result", selection=[('expectation', 'Rank of Expectation'),
                                                                ('improvement', 'Need To Improvement'),
                                                                ('meet', 'Meet'), ('exceed', 'Exceed'),
                                                                ('fail', 'Fail'), ], required=False)
    score = fields.Float(string="Score", required=False, compute='get_score', readonly=True)
    # active = fields.Boolean('Active', default=True)
    kra_kpi = fields.Char(string="KRA", )
    employee_self_assessment = fields.Float(string="Employee Self Assessment", required=False, )
    direct_manager = fields.Float(string="Direct Manager", required=False, )
    in_direct_manager = fields.Float(string="In Direct Manager", required=False, )
    interval_kpi = fields.Many2one(comodel_name="evaluation.evaluation")


    @api.onchange('direct_manager', 'in_direct_manager', 'interval_kpi')
    def get_final_total(self):
        if self.interval_kpi.evaluation_method == 'dm':
            self.percentage = self.direct_manager
        if self.interval_kpi.evaluation_method == 'average':
            self.percentage = (self.direct_manager + self.in_direct_manager) / 2
        if self.interval_kpi.evaluation_method == 'pm':
            self.percentage = 0


    @api.depends('percentage', 'kpi_weight')
    def get_score(self):
        for rec in self:
            rec.score = (rec.percentage * rec.kpi_weight)
