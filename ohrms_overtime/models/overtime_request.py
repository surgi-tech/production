# -*- coding: utf-8 -*-

from dateutil import relativedelta
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from datetime import datetime, date, timedelta, time


class AttendanceAttendance(models.Model):
    _name = 'attendance.attendance'
    _rec_name = 'employee_id'


    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee",)
    check_in = fields.Datetime(string="Check In", required=False, )
    check_out = fields.Datetime(string="Check Out", required=False, )
    work_hour = fields.Float(string="Work Hour",  required=False, )
    interval_attendance = fields.Many2one(comodel_name="hr.overtime", string="", required=False, )




class HrOverTime(models.Model):
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread']

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        sub_employees = self.env['hr.employee'].search(
            [('parent_id.user_id', '=', self.env.user.id)])
        sub_employees_ids = [it.id for it in sub_employees]
        domain = [('id', 'in', [employee.id] + sub_employees_ids)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _get_task_domain(self):
        domain = [('user_id', '=', self.env.uid)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    @api.onchange('days_no_tmp')
    def _onchange_days_no_tmp(self):
        self.days_no = self.days_no_tmp

    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id, required=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid,
                                   store=True)
    current_user_boolean = fields.Boolean()
    project_id = fields.Many2one('project.project', string="Project")
    project_manager_id = fields.Many2one('res.users', string="Project Manager")
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date to')
    days_no_tmp = fields.Float('Hours', compute="_get_days", store=True)
    days_no = fields.Float('No. of Days', store=True)
    desc = fields.Text('Description')
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft")
    cancel_reason = fields.Text('Refuse Reason')
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID")
    attchd_copy = fields.Binary('Attach A File')
    attchd_copy_name = fields.Char('File Name')
    type = fields.Selection([('cash', 'Cash'), ('leave', 'leave')], default="leave", required=True, string="Type")
    overtime_type_id = fields.Many2one('overtime.type', domain="[('type','=',type),('duration_type','=', "
                                                               "duration_type)]")
    public_holiday = fields.Boolean(default=False, compute='_onchange_date', store=True)
    is_weekend = fields.Boolean(default=False, compute='_onchange_date', store=True)
    total_morning_hours = fields.Float(compute='_get_hour_amount', store=True)
    total_night_hours = fields.Float(compute='_get_hour_amount', store=True)

    # attendance_ids = fields.Many2many('hr.attendance', string='Attendance')
    attendance_ids = fields.One2many(comodel_name="attendance.attendance",
                                     inverse_name="interval_attendance",
                                     string="", required=False)

    work_schedule = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids')
    global_leaves = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids')
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    cash_hrs_amount = fields.Float(string='Overtime Amount', compute='_get_hour_amount', store=True)
    cash_day_amount = fields.Float(string='Overtime Amount', compute='_get_hour_amount', store=True)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)

    task_id = fields.Many2one("project.task", domain=_get_task_domain)
    budget_id = fields.Many2one("overtime.budget")

    # @api.depends('current_user')
    # def check_current_user(self):
    # for i in self:
    # if self.env.user.id == self.employee_id.user_id.id:
    #     i.update({
    #         'current_user_boolean': True,
    #     })

    @api.onchange('employee_id')
    def _get_defaults(self):
        for sheet in self:
            if sheet.employee_id:
                employee_id = sheet.employee_id.sudo()
                department_id = employee_id.department_id
                job_id = employee_id.job_id
                manager_id = employee_id.parent_id
                sheet.update({
                    'department_id': department_id.id if department_id else None,
                    'job_id': job_id.id if job_id else None,
                    'manager_id': manager_id.user_id.id if manager_id and manager_id.user_id else None
                })

    @api.depends('project_id')
    def _get_project_manager(self):
        for sheet in self:
            if sheet.project_id:
                sheet.update({
                    'project_manager_id': sheet.project_id.user_id.id,
                })

    @api.depends('date_from', 'date_to')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
                if ((recd.date_to - recd.date_from).total_seconds() / 3600.0) > 24.0:
                    raise ValidationError('Over time can not be more than 24 hrs.')

        for sheet in self:
            if sheet.date_from and sheet.date_to:
                days_no_tmp = sheet.date_to - sheet.date_from
                sheet.update({
                    'days_no_tmp': days_no_tmp.total_seconds() / 3600.0 if sheet.duration_type == 'hours' else days_no_tmp.days
                })

    @api.depends('overtime_type_id')
    def _get_hour_amount(self):
        for rec in self:
            if rec.overtime_type_id.rule_line_ids:
                if rec.public_holiday:
                    for line in rec.overtime_type_id.rule_line_ids:
                        if line.name == 'holiday' and rec.duration_type == 'hours' and rec.contract_id:
                            rec.cash_hrs_amount = rec.contract_id.over_hour * line.hrs_amount * rec.days_no_tmp
                            break
                elif rec.is_weekend:
                    for line in rec.overtime_type_id.rule_line_ids:
                        if line.name == 'weekend' and rec.duration_type == 'hours' and rec.contract_id:
                            rec.cash_hrs_amount = rec.contract_id.over_hour * line.hrs_amount * rec.days_no_tmp
                            break
                else:
                    morning_rule = night_rule = None
                    for line in rec.overtime_type_id.rule_line_ids:
                        if line.name == 'working_day_morning':
                            morning_rule = line
                        elif line.name == 'working_day_night':
                            night_rule = line
                    morning_start = morning_rule.from_hrs
                    morning_end = morning_rule.to_hrs
                    night_start = morning_end
                    night_end = (morning_start - 0.01) % 24
                    total_morning_hours, total_night_hours = self._get_day_night_hours(day_start=morning_start,
                                                                                                 day_end=morning_end,
                                                                                                 night_start=night_start,
                                                                                                 night_end=night_end,
                                                                                                 interval_start=rec.date_from,
                                                                                                 interval_end=rec.date_to)
                    rec.total_morning_hours = total_morning_hours
                    rec.total_night_hours = total_night_hours
                    if rec.duration_type == 'hours' and rec.contract_id:
                        morning_rate = morning_rule.hrs_amount if morning_rule else 0
                        night_rate = night_rule.hrs_amount if night_rule else 0
                        hour_rate = rec.contract_id.over_hour

                        rec.cash_hrs_amount = (hour_rate * rec.total_morning_hours * morning_rate) \
                                               + (hour_rate * rec.total_night_hours * night_rate)



        """To be removed after handling duratoin_type == days"""
        # if self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
        #     for recd in self.overtime_type_id.rule_line_ids:
        #         if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
        #             if self.contract_id.over_day:
        #                 cash_amount = self.contract_id.over_day * recd.hrs_amount
        #                 self.cash_day_amount = cash_amount
        #             else:
        #                 raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))


    def submit_to_f(self):
        # notification to employee
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your OverTime Request Waiting Finance Approve .."
        msg = _(body)
        # if self.current_user:
        #     self.message_post(body=msg, partner_ids=recipient_partners)

        # notification to finance :
        group = self.env.ref('account.group_account_invoice', False)
        recipient_partners = []
        # for recipient in group.users:
        #     recipient_partners.append((4, recipient.partner_id.id))

        body = "You Get New Time in Lieu Request From Employee : " + str(
            self.employee_id.name)
        msg = _(body)
        # self.message_post(body=msg, partner_ids=recipient_partners)
        return self.sudo().write({
            'state': 'f_approve'
        })

    # def approve(self):
    #     return self.sudo().write({
    #         'state': 'approved',
    #     })

    def approve(self):
        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': day_hour,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(
                holiday_vals)
            self.leave_id = holiday.id

        elif self.overtime_type_id.type == 'cash':
            request_date = self.date_from.date()
            if not self.budget_id.date_from <= request_date <= self.budget_id.date_to:
                raise ValidationError("Request date is out budget period.")

            employee_budget_line = self.env['overtime.employee.budget'].search([('employee_id', '=', self.employee_id.id),
                                                                                ('budget_id', '=', self.budget_id.id)])
            department_budget_line = self.env['overtime.department.budget'].search([('department_id', '=', self.department_id.id),
                                                                                    ('budget_id', '=', self.budget_id.id)])

            flag1 = flag2 = False
            if employee_budget_line and (employee_budget_line[0].consumed_amount + self.cash_hrs_amount) <= employee_budget_line[0].amount:
                flag1 = True

            if department_budget_line and (department_budget_line[0].consumed_amount + self.cash_hrs_amount) <= department_budget_line[0].amount:
                flag2 = True

            if flag1 and flag2:
                employee_budget_line[0].consumed_amount += self.cash_hrs_amount
                department_budget_line[0].consumed_amount += self.cash_hrs_amount
                self.budget_id.consumed_budget += self.cash_hrs_amount

            elif not flag1:
                raise ValidationError("This Employee is not added to this budget or have exceeded his limit")

            elif not flag2:
                raise ValidationError("This Employee's department is not added to this budget or have exceeded the department limit.")

        # notification to employee :
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your Time In Lieu Request Has been Approved ..."
        msg = _(body)
        # self.message_post(body=msg, partner_ids=recipient_partners)
        return self.sudo().write({
            'state': 'approved',

        })

        # return {
        #     'name': _('Leave Adjust'),
        #     'context': {'default_til_id': self.id},
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'leave.adjust',
        #     'view_id': self.env.ref('leave_management.leave_adjust_wizard_view',
        #                             False).id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        # }

    def reject(self):

        self.state = 'refused'
        # return {
        #     'name': _('Refuse Business Trip'),
        #     'context': {'default_overtime_id': self.id},
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'refuse.wzrd',
        #     'view_id': self.env.ref('leave_management.refuse_wzrd_view',
        #                             False).id,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'target': 'new',
        # }

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
        values['name'] = seq
        return super(HrOverTime, self.sudo()).create(values)

    def unlink(self):
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super(HrOverTime, self).unlink()

    @api.depends('date_from', 'date_to', 'employee_id')
    def _onchange_date(self):
        for rec in self:
            holiday = False
            lines = [(5, 0, 0)]
            if rec.contract_id and rec.date_from and rec.date_to:
                for leaves in rec.contract_id.resource_calendar_id.global_leave_ids:
                    if leaves.date_from <= rec.date_from <= leaves.date_to:
                        holiday = True

                week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                start_day_no = week_days.index(rec.date_from.strftime("%A").lower())
                _is_weekend = True
                for att in rec.contract_id.resource_calendar_id.attendance_ids:
                    if str(att.dayofweek) == str(start_day_no):
                        _is_weekend = False
                        break

                if holiday:
                    rec.write({
                        'public_holiday': True,
                        'is_weekend': False
                    })
                else:
                    rec.write({'public_holiday': False})
                    rec.is_weekend = _is_weekend

                hr_attendance = self.env['hr.attendance'].search([('employee_id', '=', rec.employee_id.id)])

                for emp_att in hr_attendance:
                    checkin = datetime.strptime(str(emp_att.check_in), '%Y-%m-%d %H:%M:%S').date()
                    start_date = datetime.strptime(str(rec.date_from), '%Y-%m-%d %H:%M:%S').date()
                    to_date = datetime.strptime(str(rec.date_to), '%Y-%m-%d %H:%M:%S').date()

                    if start_date<=checkin<=to_date:
                        print(start_date,checkin,to_date,'QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ')
                        lines.append((0, 0, {
                        'employee_id':emp_att.employee_id.id ,
                        'check_in': emp_att.check_in,
                        'check_out': emp_att.check_out,
                        'work_hour': emp_att.worked_hours,
                    }))

                # [(6, 0, hr_attendance.ids)]
                rec.update({
                    'attendance_ids': lines
                })

    @api.constrains('date_from', 'date_to', 'attendance_ids')
    def _validate_check_out_date(self):
        for res in self.attendance_ids:
            if self.date_to > res.check_out:
                raise ValidationError('check out in attendance must be greater than Date To in Overtime Request')

            if self.date_from < res.check_in:
                raise ValidationError('check in in attendance must be less than Date From in Overtime Request')

    def _get_day_night_hours(self,
                             day_start: float, day_end: float,
                             night_start: float, night_end: float,
                             interval_start: datetime, interval_end: datetime):
        if day_end != night_start:
            raise ValidationError("There is an empty gap in day/night configuration.")

        # TODO: fix hardcode +2 timezone
        interval_start = interval_start + timedelta(hours=2)
        interval_end = interval_end + timedelta(hours=2)

        interval_start_time = interval_start.time().hour + (interval_start.time().minute / 60.0)
        interval_end_time = interval_end.time().hour + (interval_end.time().minute / 60.0)

        interval_start_morning = interval_end_morning = False

        if day_start <= interval_start_time < day_end:
            interval_start_morning = True

        if day_start < interval_end_time <= day_end:
            interval_end_morning = True

        total_interval_time_hours = (interval_end - interval_start).total_seconds() / 3600.0
        total_morning_hours = total_night_hours = 0
        morning_hours = (day_end - day_start) % 24
        night_hours = 24 - morning_hours

        if interval_start_morning and interval_end_morning:
            if total_interval_time_hours <= morning_hours:
                total_morning_hours = total_interval_time_hours
                total_night_hours = 0
            else:
                total_night_hours = night_hours
                total_morning_hours = total_interval_time_hours - night_hours
                total_morning_hours = total_morning_hours if total_morning_hours > 0 else 0
        elif not interval_start_morning and not interval_end_morning:
            if total_interval_time_hours <= night_hours:
                total_night_hours = total_interval_time_hours
                total_morning_hours = 0
            else:
                total_morning_hours = morning_hours
                total_night_hours = total_interval_time_hours - morning_hours
                total_night_hours = total_night_hours if total_night_hours > 0 else 0
        elif interval_start_morning and not interval_end_morning:
            total_morning_hours = (day_end - interval_start_time) % 24
            total_night_hours = total_interval_time_hours - total_morning_hours
            total_night_hours = total_night_hours if total_night_hours > 0 else 0
        else:
            total_night_hours = (night_end - interval_start_time) % 24
            total_morning_hours = total_interval_time_hours - total_night_hours
            total_morning_hours = total_morning_hours if total_morning_hours > 0 else 0

        return total_morning_hours, total_night_hours

class HrOverTimeType(models.Model):
    _name = 'overtime.type'

    name = fields.Char('Name')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')])

    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type', domain="[('id', 'in', leave_compute)]")
    leave_compute = fields.Many2many('hr.leave.type', compute="_get_leave_type")
    rule_line_ids = fields.One2many('overtime.type.rule', 'type_line_id')

    @api.onchange('duration_type')
    def _get_leave_type(self):
        dur = ''
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute = ids


class HrOverTimeTypeRule(models.Model):
    _name = 'overtime.type.rule'

    type_line_id = fields.Many2one('overtime.type', string='Over Time Type')
    name = fields.Selection([('working_day_morning', 'Working Day (Morning)'),
                             ('working_day_night', 'Working Day (Night)'),
                             ('weekend', 'Week End'),
                             ('holiday', 'Holiday')],
                            string='Name')
    from_hrs = fields.Float('From', required=True, default=0)
    to_hrs = fields.Float('To', required=True, default=23.99)
    hrs_amount = fields.Float('Rate', required=True)
