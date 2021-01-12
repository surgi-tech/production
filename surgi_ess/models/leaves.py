
from datetime import datetime, timedelta
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError



class HRLeave(models.Model):
    _inherit = 'hr.leave'

    def action_allocation_confirm(self):
        pass

    
    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        if self.holiday_status_id.request_unit=='hour':
            self.request_unit_hours=True
        else:
            self.request_unit_hours = False


    # @api.constrains('holiday_status_id','request_hour_from','request_hour_to')
    # def compute_prevent_permission_con(self):
    #
    #     diff_hour=0.0
    #     diff_permission_hour=0.0
    #     if self.request_unit_hours:
    #         diff_hour=float(str(self.request_hour_to))-float(str(self.request_hour_from))
    #     if self.holiday_status_id.limited_hours==True:
    #
    #         if self.holiday_status_id.mini_hours<=diff_hour<=self.holiday_status_id.max_hours:
    #             pass
    #         else:
    #             raise ValidationError(_('Not allowed hours'))






    def _compute_show_leaves(self):
        show_leaves = self.env['res.users'].has_group('hr_holidays.group_hr_holidays_user')
        for employee in self:
            if show_leaves or employee.user_id == self.env.user:
                employee.show_leaves = True
            else:
                employee.show_leaves = False

    current_user = fields.Many2one('res.users', compute='_get_current_user')


    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        # i think this work too so you don't have to loop
        # self.update({'current_user': self.env.user.id})

    # @api.onchange('holiday_status_id')
    # def _onchange_holiday_status_id(self):
    #     self._onchange_date_to()


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    limited_hours = fields.Boolean(string="Limited Hours",  )
    mini_hours = fields.Float(string="Mini Hours",  required=False, )
    max_hours = fields.Float(string="Max Hours",  required=False, )

    @api.constrains('mini_hours','max_hours')
    def prevent_mini_max_hours(self):

        if self.limited_hours:
            if self.mini_hours>self.max_hours:
                raise ValidationError(_('Minimum hours Must be less than Maximum hours'))
