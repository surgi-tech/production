# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api
from datetime import datetime,timedelta
#from odoo.exceptions import UserError

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_before_day_alert = fields.Boolean("Leave before day alert")
    leave_before_days = fields.Integer("Leave before days")
                                                                    
class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # @api.multi
    @api.onchange('holiday_status_id','date_from','employee_id')
    def date_from_onchange(self): 
    
        if self and self.holiday_status_id and self.date_from and self.employee_id :
            hol_status_obj = self.env['hr.leave.type'].search([('id','=',self.holiday_status_id.id)],limit= 1 )
    
            if hol_status_obj:
                if hol_status_obj.leave_before_day_alert and hol_status_obj.leave_before_days:

                    if not ( self.user_has_groups('hr.group_hr_manager') and (self.employee_id.user_id and self.env.user.id != self.employee_id.user_id.id) ):
                        leave_from  = datetime.strptime( str(self.date_from), "%Y-%m-%d %H:%M:%S") - timedelta(days = hol_status_obj.leave_before_days )
                        
                        if (datetime.now().date() > leave_from.date() ):
                            self.update({'date_from': False })                        
                                                        
                            warning_mess = {
                                
                                'message' : ('You can apply ' + self.holiday_status_id.name + ' before ' + str(hol_status_obj.leave_before_days) + ' days. Please contact your manager for further approval.'),
                                'title': "Warning" 
                            }
                            return {'warning': warning_mess}
