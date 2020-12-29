# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2020.
#    Author: Eng.Ramadan Khalil (<rkhalil1990@gmail.com>)
#    website': https://www.linkedin.com/in/ramadan-khalil-a7088164
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import pytz
from datetime import datetime, date, timedelta, time


class AttendanceSheet(models.Model):
    _inherit = 'attendance.sheet'

    penalty_ids = fields.One2many('hr.attendance.penalty', 'sheet_id',
                                  'Penalities')
    penalty_count = fields.Integer('Penalties Count',
                                   compute='compute_penalty_count')
    accrual_date = fields.Date('Accrual Date', required=False)
    no_miss = fields.Integer(compute="_compute_sheet_total",
                             string="No of Miss Punches", readonly=True,
                             store=True)
    tot_miss = fields.Float(compute="_compute_sheet_total",
                            string="Total Miss Punches Penalty", readonly=True,
                            store=True)
    tot_shift_allowance = fields.Float(compute="_compute_sheet_total",
                            string="Total Shift Allowance", readonly=True,
                            store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved'),
        ('cancel', 'Cancel')], default='draft', track_visibility='onchange',
        string='Status', required=True, readonly=True, index=True,
        help=' * The \'Draft\' status is used when a HR user is creating a new  attendance sheet. '
             '\n* The \'Confirmed\' status is used when  attendance sheet is confirmed by HR user.'
             '\n* The \'Approved\' status is used when  attendance sheet is accepted by the HR Manager.')

    @api.depends('line_ids.overtime', 'line_ids.diff_time', 'line_ids.late_in')
    def _compute_sheet_total(self):
        res = super(AttendanceSheet, self)._compute_sheet_total()
        for sheet in self:
            miss_line_ids = sheet.line_ids.filtered(
                lambda l: l.miss_type != 'right' and l.miss_pen > 0)
            sheet.no_miss = len(miss_line_ids)
            sheet.tot_miss = sum([l.miss_pen for l in miss_line_ids])
            sheet.tot_shift_allowance  =sum([l.shift_allowance for l in sheet.line_ids])
        return res

    def compute_penalty_count(self):
        for sheet in self:
            sheet.penalty_count = len(sheet.penalty_ids)

    def action_approve(self):
        self.action_create_penalties()
        self.write({'state': 'done'})

    def action_cancel(self):
        for sheet in self:
            if sheet.penalty_ids:
                for pen in sheet.penalty_ids:
                    if pen.paid:
                        raise ValidationError(_('You cannot cancel attendance '
                                                'sheet as there is a penalty '
                                                'that has already paid'))
                    pen.unlink()
            sheet.write({'state': 'cancel'})

    def action_create_penalties(self):
        for sheet in self:
            if not sheet.accrual_date:
                raise ValidationError(_('Please Set accrual Date First'))
            late_lines = sheet.line_ids.filtered(lambda l: l.late_in > 0)
            penalty_obj = self.env['hr.attendance.penalty']
            for lateline in late_lines:
                values = {
                    'employee_id': sheet.employee_id.id,
                    'type': 'late',
                    'accrual_date': sheet.accrual_date,
                    'date': lateline.date,
                    'sheet_id': sheet.id,
                    'name': 'Late IN',
                    'amount': lateline.late_in
                }
                penalty_obj.create(values)

            absence_lines = sheet.line_ids.filtered(
                lambda l: l.diff_time > 0 and l.status == "ab")
            for abline in absence_lines:
                values = {
                    'employee_id': sheet.employee_id.id,
                    'type': 'ab',
                    'accrual_date': sheet.accrual_date,
                    'date': abline.date,
                    'sheet_id': sheet.id,
                    'name': 'Absence',
                    'amount': abline.diff_time
                }
                penalty_obj.create(values)

            diff = sheet.line_ids.filtered(
                lambda l: l.diff_time > 0 and l.status != "ab")
            for diffline in diff:
                values = {
                    'employee_id': sheet.employee_id.id,
                    'type': 'ab',
                    'accrual_date': sheet.accrual_date,
                    'date': diffline.date,
                    'sheet_id': sheet.id,
                    'name': 'diff',
                    'amount': diffline.diff_time
                }
                penalty_obj.create(values)
            miss_lines = sheet.line_ids.filtered(
                lambda l: l.miss_type != 'right' and l.miss_pen > 0)
            for missline in miss_lines:
                values = {
                    'employee_id': sheet.employee_id.id,
                    'type': 'mis',
                    'accrual_date': sheet.accrual_date,
                    'date': missline.date,
                    'sheet_id': sheet.id,
                    'name': 'Miss-Punch Penalty',
                    'amount': missline.miss_pen
                }
                penalty_obj.create(values)

    @api.model
    def cron_update_attendance_sheet(self):
        sheet_ids = self.search([('state', '=', 'draft')])
        for sheet in sheet_ids:
            sheet.get_attendances()

    def get_attendance_intervals(self, employee, day_start, day_end, tz):
        """

        :param employee:
        :param day_start:datetime the start of the day in datetime format
        :param day_end: datetime the end of the day in datetime format
        :return:
        """
        day_start_native = day_start.replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)
        day_end_native = day_end.replace(tzinfo=tz).astimezone(
            pytz.utc).replace(tzinfo=None)
        res = []
        domain = [('employee_id.id', '=', employee.id),
                  ('check_in', '>=', day_start_native),
                  ('check_in', '<=', day_end_native), ]
        if employee.attendance_approval:
            domain += [('approval_state', '=', 'approved')]
        attendances = self.env['hr.attendance'].sudo().search(domain,
                                                              order="check_in")
        for att in attendances:
            check_in = att.check_in
            check_out = att.check_out
            if not check_out:
                continue
            res.append((check_in, check_out, att.state))
        return res

    def get_attendances(self):
        for att_sheet in self:
            contract = att_sheet.contract_id
            att_sheet.line_ids.unlink()
            shift_allowance = contract.shift_allowance
            att_line = self.env["attendance.sheet.line"]
            from_date = att_sheet.date_from
            to_date = att_sheet.date_to
            today = datetime.today().date()
            if to_date > today:
                to_date = today
            emp = att_sheet.employee_id
            tz = pytz.timezone(emp.tz)
            if not tz:
                raise ValidationError(
                    "Please add time zone for employee : %s" % emp.name)
            calendar_id = emp.contract_id.resource_calendar_id
            if not calendar_id:
                raise ValidationError(_(
                    'Please add working hours to the %s `s contract ' % emp.name))
            policy_id = att_sheet.att_policy_id
            if not policy_id:
                raise ValidationError(_(
                    'Please add Attendance Policy to the %s `s contract ' % emp.name))

            all_dates = [(from_date + timedelta(days=x)) for x in
                         range((to_date - from_date).days + 1)]
            abs_cnt = 0
            miss_cnt = 0
            late_cnt = []
            diff_cnt = []
            for day in all_dates:
                day_start = datetime(day.year, day.month, day.day)
                day_end = day_start.replace(hour=23, minute=59,
                                            second=59)
                day_str = str(day.weekday())
                date = day.strftime('%Y-%m-%d')
                if contract.multi_shift:
                    work_intervals = att_sheet.employee_id.get_employee_shifts(
                        day_start,
                        day_end, tz)
                    if not work_intervals:
                        work_intervals = calendar_id.att_get_work_intervals(
                            day_start,
                            day_end, tz)

                    work_intervals = calendar_id.att_interval_clean(
                        work_intervals)

                else:
                    work_intervals = calendar_id.att_get_work_intervals(
                        day_start,
                        day_end, tz)
                attendance_intervals = self.get_attendance_intervals(emp,
                                                                     day_start,
                                                                     day_end,
                                                                     tz)
                leaves = self._get_emp_leave_intervals(emp, day_start, day_end)
                public_holiday = self.get_public_holiday(date, emp)
                reserved_intervals = []
                overtime_policy = policy_id.get_overtime()
                abs_flag = False
                if work_intervals:
                    if public_holiday:
                        if attendance_intervals:
                            for attendance_interval in attendance_intervals:
                                shift_alw_amount =0
                                if shift_allowance:
                                    shift_alw_amount = policy_id.get_shift_allowance(
                                        attendance_interval[0],
                                        attendance_interval[1], tz)
                                overtime = attendance_interval[1] - \
                                           attendance_interval[0]
                                float_overtime = overtime.total_seconds() / 3600
                                if float_overtime <= overtime_policy[
                                    'ph_after']:
                                    act_float_overtime = float_overtime = 0
                                else:
                                    act_float_overtime = (float_overtime -
                                                          overtime_policy[
                                                              'ph_after'])
                                    float_overtime = (float_overtime -
                                                      overtime_policy[
                                                          'ph_after']) * \
                                                     overtime_policy['ph_rate']
                                ac_sign_in = pytz.utc.localize(
                                    attendance_interval[0]).astimezone(tz)
                                float_ac_sign_in = self._get_float_from_time(
                                    ac_sign_in)
                                ac_sign_out = pytz.utc.localize(
                                    attendance_interval[1]).astimezone(tz)
                                worked_hours = attendance_interval[1] - \
                                               attendance_interval[0]
                                float_worked_hours = worked_hours.total_seconds() / 3600
                                float_ac_sign_out = float_ac_sign_in + float_worked_hours
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'ac_sign_in': float_ac_sign_in,
                                    'ac_sign_out': float_ac_sign_out,
                                    'worked_hours': float_worked_hours,
                                    'shift_allowance':shift_alw_amount,
                                    # 'o_worked_hours': float_worked_hours,
                                    'overtime': float_overtime,
                                    'act_overtime': act_float_overtime,
                                    'att_sheet_id': self.id,
                                    'status': 'ph',
                                    'note': _("working on Public Holiday")
                                }
                                att_line.create(values)
                        else:
                            values = {
                                'date': date,
                                'day': day_str,
                                'att_sheet_id': self.id,
                                'status': 'ph',
                            }
                            att_line.create(values)
                    else:
                        if any([att[2] != 'right' for att in
                                attendance_intervals]):
                            act_float_miss_overtime = 0
                            float_miss_overtime = 0
                            policy_miss_diff = 0
                            act_float_miss_diff = 0
                            act_float_miss_late = 0
                            policy_miss_late = 0

                            all_miss_intervals = attendance_intervals
                            miss_cnt += 1
                            shift_alw_amount = 0
                            miss_amount = policy_id.get_miss(miss_cnt)
                            for i, work_interval in enumerate(work_intervals):
                                pl_sign_in = self._get_float_from_time(
                                    pytz.utc.localize(
                                        work_interval[0]).astimezone(tz))
                                pl_sign_out = self._get_float_from_time(
                                    pytz.utc.localize(
                                        work_interval[1]).astimezone(tz))
                                ac_sign_in = ac_sign_out = 0
                                miss_att_intervals = []
                                miss_type = 'right'
                                note = ''
                                for j, miss_att in enumerate(
                                        all_miss_intervals):
                                    if miss_att[0] < work_interval[1] and \
                                            miss_att[2] == 'fixout':
                                        miss_att_intervals.append(
                                            all_miss_intervals.pop(j))
                                    elif miss_att[1] >= work_interval[0] and \
                                            miss_att[2] == 'fixin':
                                        if i + 1 < len(work_intervals):
                                            next_work_interval = work_intervals[
                                                i + 1]
                                            if miss_att[1] >= \
                                                    next_work_interval[0]:
                                                continue
                                        else:
                                            miss_att_intervals.append(
                                                all_miss_intervals.pop(j))
                                if miss_att_intervals and miss_att_intervals[0][
                                    2] != 'fixin':
                                    miss_type = 'missout'
                                    if leaves:
                                        for leave_interval in leaves:
                                            if leave_interval[0] < \
                                                    work_interval[1] < \
                                                    leave_interval[1]:
                                                miss_type = 'right'
                                                miss_amount = 0
                                                miss_cnt -= 1
                                                note = 'Removing Mis-punch Out due to leave'

                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(miss_att_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = 0
                                    miss_lat_in_interval = (
                                        work_interval[0],
                                        miss_att_intervals[0][0])
                                    miss_late_in = timedelta(0, 0, 0)
                                    if leaves:
                                        miss_late_clean_intervals = calendar_id.att_interval_without_leaves(
                                            miss_lat_in_interval, leaves)
                                        for late_clean in miss_late_clean_intervals:
                                            miss_late_in += late_clean[1] - \
                                                            late_clean[0]
                                    else:
                                        miss_late_in = (
                                                miss_att_intervals[0][0] -
                                                work_interval[0])
                                    float_miss_late = miss_late_in.total_seconds() / 3600
                                    act_float_miss_late = float_miss_late
                                    policy_miss_late, late_cnt = policy_id.get_late(
                                        float_miss_late, late_cnt)

                                elif miss_att_intervals and \
                                        miss_att_intervals[-1][2] != 'fixout':
                                    miss_type = 'misin'
                                    if leaves:
                                        for leave_interval in leaves:
                                            if leave_interval[0] < \
                                                    work_interval[0] < \
                                                    leave_interval[1]:
                                                miss_type = 'right'
                                                miss_amount = 0
                                                miss_cnt -= 1
                                                note = 'Removing Mis-punch In due to leave'
                                    ac_sign_in = 0
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(
                                            miss_att_intervals[-1][
                                                1]).astimezone(tz))
                                    overtime_interval = (
                                        work_interval[1],
                                        miss_att_intervals[-1][1])
                                    miss_diff_interval = (
                                        miss_att_intervals[-1][1],
                                        work_interval[1]
                                    )
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        miss_overtime = timedelta(hours=0,
                                                                  minutes=0,
                                                                  seconds=0)

                                    else:
                                        miss_overtime = overtime_interval[1] - \
                                                        overtime_interval[0]

                                    float_miss_overtime = miss_overtime.total_seconds() / 3600
                                    if float_miss_overtime <= overtime_policy[
                                        'wd_after']:
                                        act_float_miss_overtime = float_miss_overtime = 0
                                    else:
                                        act_float_miss_overtime = float_miss_overtime
                                        float_miss_overtime = float_miss_overtime * \
                                                              overtime_policy[
                                                                  'wd_rate']
                                    miss_diff_time = timedelta(hours=0,
                                                               minutes=0,
                                                               seconds=0)
                                    if miss_diff_interval[0] < \
                                            miss_diff_interval[1]:
                                        if leaves:
                                            miss_diff_clean_intervals = calendar_id.att_interval_without_leaves(
                                                miss_diff_interval, leaves)
                                            for diff_clean in miss_diff_clean_intervals:
                                                miss_diff_time += diff_clean[
                                                                      1] - \
                                                                  diff_clean[0]
                                        else:
                                            miss_diff_time = (
                                                    miss_diff_interval[1] -
                                                    miss_diff_interval[0])

                                    float_miss_diff = miss_diff_time.total_seconds() / 3600
                                    act_float_miss_diff = float_miss_diff
                                    policy_miss_diff, diff_cnt = policy_id.get_diff(
                                        float_miss_diff, diff_cnt)

                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'pl_sign_in': pl_sign_in,
                                    'pl_sign_out': pl_sign_out,
                                    'ac_sign_in': ac_sign_in,
                                    'ac_sign_out': ac_sign_out,
                                    'miss_type': miss_type,
                                    'late_in': policy_miss_late,
                                    'act_late_in': act_float_miss_late,
                                    'overtime': float_miss_overtime,
                                    'act_overtime': act_float_miss_overtime,
                                    'diff_time': policy_miss_diff,
                                    'act_diff_time': act_float_miss_diff,
                                    'miss_pen': miss_amount,
                                    'status': '',
                                    'note': note,
                                    'att_sheet_id': self.id

                                }
                                att_line.create(values)
                            continue

                        for i, work_interval in enumerate(work_intervals):
                            float_worked_hours = 0
                            att_work_intervals = []
                            diff_intervals = []
                            late_in_interval = []
                            shift_alw_amount = 0
                            diff_time = timedelta(hours=00, minutes=00,
                                                  seconds=00)
                            late_in = timedelta(hours=00, minutes=00,
                                                seconds=00)
                            overtime = timedelta(hours=00, minutes=00,
                                                 seconds=00)
                            for j, att_interval in enumerate(
                                    attendance_intervals):
                                if max(work_interval[0], att_interval[0]) < min(
                                        work_interval[1], att_interval[1]):
                                    current_att_interval = att_interval
                                    if i + 1 < len(work_intervals):
                                        next_work_interval = work_intervals[
                                            i + 1]
                                        if max(next_work_interval[0],
                                               current_att_interval[0]) < min(
                                            next_work_interval[1],
                                            current_att_interval[1]):
                                            split_att_interval = (
                                                next_work_interval[0],
                                                current_att_interval[1])
                                            current_att_interval = (
                                                current_att_interval[0],
                                                next_work_interval[0])
                                            attendance_intervals[
                                                j] = current_att_interval
                                            attendance_intervals.insert(j + 1,
                                                                        split_att_interval)
                                    att_work_intervals.append(
                                        current_att_interval)
                            reserved_intervals += att_work_intervals
                            pl_sign_in = self._get_float_from_time(
                                pytz.utc.localize(work_interval[0]).astimezone(
                                    tz))
                            pl_sign_out = self._get_float_from_time(
                                pytz.utc.localize(work_interval[1]).astimezone(
                                    tz))
                            ac_sign_in = 0
                            ac_sign_out = 0
                            status = ""
                            note = ""
                            if att_work_intervals:
                                if shift_allowance:
                                    for attw_interval in attendance_intervals:
                                        shift_alw_amount+=policy_id.get_shift_allowance(attw_interval[0],attw_interval[1],tz)
                                if len(att_work_intervals) > 1:
                                    # print("there is more than one interval for that work interval")
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    remain_interval = (
                                        att_work_intervals[0][1],
                                        work_interval[1])
                                    # print'first remain intervals is',remain_interval
                                    for att_work_interval in att_work_intervals:
                                        float_worked_hours += (
                                                                      att_work_interval[
                                                                          1] -
                                                                      att_work_interval[
                                                                          0]).total_seconds() / 3600
                                        # print'float worked hors is', float_worked_hours
                                        if att_work_interval[1] <= \
                                                remain_interval[0]:
                                            continue
                                        if att_work_interval[0] >= \
                                                remain_interval[1]:
                                            break
                                        if remain_interval[0] < \
                                                att_work_interval[0] < \
                                                remain_interval[1]:
                                            diff_intervals.append((
                                                remain_interval[
                                                    0],
                                                att_work_interval[
                                                    0]))
                                            remain_interval = (
                                                att_work_interval[1],
                                                remain_interval[1])
                                    if remain_interval and remain_interval[0] <= \
                                            work_interval[1]:
                                        diff_intervals.append((remain_interval[
                                                                   0],
                                                               work_interval[
                                                                   1]))
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = ac_sign_in + ((
                                                                        att_work_intervals[
                                                                            -1][
                                                                            1] -
                                                                        att_work_intervals[
                                                                            0][
                                                                            0]).total_seconds() / 3600)
                                else:
                                    late_in_interval = (
                                        work_interval[0],
                                        att_work_intervals[0][0])
                                    overtime_interval = (
                                        work_interval[1],
                                        att_work_intervals[-1][1])
                                    if overtime_interval[1] < overtime_interval[
                                        0]:
                                        overtime = timedelta(hours=0, minutes=0,
                                                             seconds=0)
                                        diff_intervals.append((
                                            overtime_interval[
                                                1],
                                            overtime_interval[
                                                0]))
                                    else:
                                        overtime = overtime_interval[1] - \
                                                   overtime_interval[0]
                                    ac_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              0]).astimezone(
                                            tz))
                                    ac_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(att_work_intervals[0][
                                                              1]).astimezone(
                                            tz))
                                    worked_hours = att_work_intervals[0][1] - \
                                                   att_work_intervals[0][0]
                                    print(worked_hours)
                                    float_worked_hours = worked_hours.total_seconds() / 3600
                                    # ac_sign_out = ac_sign_in + float_worked_hours
                            else:
                                late_in_interval = []
                                diff_intervals.append(
                                    (work_interval[0], work_interval[1]))

                                status = "ab"
                            if diff_intervals:
                                for diff_in in diff_intervals:
                                    if leaves:
                                        status = "leave"
                                        diff_clean_intervals = calendar_id.att_interval_without_leaves(
                                            diff_in, leaves)
                                        for diff_clean in diff_clean_intervals:
                                            diff_time += diff_clean[1] - \
                                                         diff_clean[0]
                                    else:
                                        diff_time += diff_in[1] - diff_in[0]
                            if late_in_interval:
                                if late_in_interval[1] < late_in_interval[0]:
                                    late_in = timedelta(hours=0, minutes=0,
                                                        seconds=0)
                                else:
                                    if leaves:
                                        late_clean_intervals = calendar_id.att_interval_without_leaves(
                                            late_in_interval, leaves)
                                        for late_clean in late_clean_intervals:
                                            late_in += late_clean[1] - \
                                                       late_clean[0]
                                    else:
                                        late_in = late_in_interval[1] - \
                                                  late_in_interval[0]
                            float_overtime = overtime.total_seconds() / 3600
                            if float_overtime <= overtime_policy['wd_after']:
                                act_float_overtime = float_overtime = 0
                            else:
                                act_float_overtime = float_overtime
                                float_overtime = float_overtime * \
                                                 overtime_policy[
                                                     'wd_rate']
                            float_late = late_in.total_seconds() / 3600
                            act_float_late = late_in.total_seconds() / 3600
                            policy_late, late_cnt = policy_id.get_late(
                                float_late, late_cnt)
                            float_diff = diff_time.total_seconds() / 3600
                            if status == 'ab':
                                if not abs_flag:
                                    abs_cnt += 1
                                abs_flag = True

                                act_float_diff = float_diff
                                float_diff = policy_id.get_absence(float_diff,
                                                                   abs_cnt)
                            else:
                                act_float_diff = float_diff
                                float_diff, diff_cnt = policy_id.get_diff(
                                    float_diff, diff_cnt)
                            values = {
                                'date': date,
                                'day': day_str,
                                'pl_sign_in': pl_sign_in,
                                'pl_sign_out': pl_sign_out,
                                'ac_sign_in': ac_sign_in,
                                'ac_sign_out': ac_sign_out,
                                'late_in': policy_late,
                                'shift_allowance':shift_alw_amount,
                                'act_late_in': act_float_late,
                                'worked_hours': float_worked_hours,
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'diff_time': float_diff,
                                'act_diff_time': act_float_diff,
                                'status': status,
                                'att_sheet_id': self.id
                            }
                            att_line.create(values)
                        out_work_intervals = [x for x in attendance_intervals if
                                              x not in reserved_intervals]
                        if out_work_intervals:
                            for att_out in out_work_intervals:
                                overtime = att_out[1] - att_out[0]
                                ac_sign_in = self._get_float_from_time(
                                    pytz.utc.localize(att_out[0]).astimezone(
                                        tz))
                                ac_sign_out = self._get_float_from_time(
                                    pytz.utc.localize(att_out[1]).astimezone(
                                        tz))
                                float_worked_hours = overtime.total_seconds() / 3600
                                ac_sign_out = ac_sign_in + float_worked_hours
                                float_overtime = overtime.total_seconds() / 3600
                                if float_overtime <= overtime_policy[
                                    'wd_after']:
                                    float_overtime = act_float_overtime = 0
                                else:
                                    act_float_overtime = float_overtime
                                    float_overtime = act_float_overtime * \
                                                     overtime_policy['wd_rate']
                                values = {
                                    'date': date,
                                    'day': day_str,
                                    'pl_sign_in': 0,
                                    'pl_sign_out': 0,
                                    'ac_sign_in': ac_sign_in,
                                    'ac_sign_out': ac_sign_out,
                                    'overtime': float_overtime,
                                    'worked_hours': float_worked_hours,
                                    'act_overtime': act_float_overtime,
                                    'note': _("overtime out of work intervals"),
                                    'att_sheet_id': self.id
                                }
                                att_line.create(values)
                else:
                    if attendance_intervals:
                        # print "thats weekend be over time "
                        for attendance_interval in attendance_intervals:
                            overtime = attendance_interval[1] - \
                                       attendance_interval[0]
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            float_overtime = overtime.total_seconds() / 3600
                            if float_overtime <= overtime_policy['we_after']:
                                float_overtime = 0
                                act_float_overtime = 0
                            else:
                                act_float_overtime = float_overtime
                                float_overtime = act_float_overtime * \
                                                 overtime_policy['we_rate']
                            ac_sign_in = pytz.utc.localize(
                                attendance_interval[0]).astimezone(tz)
                            ac_sign_out = pytz.utc.localize(
                                attendance_interval[1]).astimezone(tz)
                            worked_hours = attendance_interval[1] - \
                                           attendance_interval[0]
                            float_worked_hours = worked_hours.total_seconds() / 3600
                            values = {
                                'date': date,
                                'day': day_str,
                                'ac_sign_in': self._get_float_from_time(
                                    ac_sign_in),
                                'ac_sign_out': self._get_float_from_time(
                                    ac_sign_out),
                                'overtime': float_overtime,
                                'act_overtime': act_float_overtime,
                                'worked_hours': float_worked_hours,
                                'att_sheet_id': self.id,
                                'status': 'weekend',
                                'note': _("working in weekend")
                            }
                            att_line.create(values)
                    else:
                        values = {
                            'date': date,
                            'day': day_str,
                            'att_sheet_id': self.id,
                            'status': 'weekend',
                            'note': ""
                        }
                        att_line.create(values)

    def action_view_penalties(self):
        penalty_ids = self.mapped('penalty_ids')
        action = self.env.ref(
            'surgi_attendance_sheet.hr_attendance_penalty_view_action').read()[
            0]
        action['domain'] = [('id', 'in', penalty_ids.ids)]
        return action


class AttendanceSheetLine(models.Model):
    _inherit = 'attendance.sheet.line'

    miss_type = fields.Selection(
        selection=[('misin', 'Miss-IN'), ('missout', 'Miss-Out'),
                   ('right', 'Right')], string='Miss Punch Type',
        default='right')
    miss_pen = fields.Float("Miss punch Penalty", readonly=True)
    shift_allowance = fields.Float('Shift Allowance')
