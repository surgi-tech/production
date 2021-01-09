# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, http, models, _
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from geopy import distance


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    location_restriction = fields.Boolean(
        string='Attendance Location Restriction')
    longitude = fields.Char(string="Longitude")
    latitude = fields.Char(string="Latitude")
    max_attendance_distance = fields.Char(
        string='Max Attendance location Distance')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        location_restriction = self.env['ir.config_parameter'].sudo().get_param(
            'emp_attendance_map_advance_app.location_restriction')
        longitude = self.env['ir.config_parameter'].sudo().get_param(
            'emp_attendance_map_advance_app.longitude')
        latitude = self.env['ir.config_parameter'].sudo().get_param(
            'emp_attendance_map_advance_app.latitude')
        max_distance = self.env['ir.config_parameter'].sudo().get_param(
            'emp_attendance_map_advance_app.max_attendance_distance')
        res.update(
            location_restriction=location_restriction,
            longitude=longitude,
            latitude=latitude,
            max_attendance_distance=max_distance
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'emp_attendance_map_advance_app.location_restriction',
            self.location_restriction)
        self.env['ir.config_parameter'].sudo().set_param(
            'emp_attendance_map_advance_app.latitude', self.latitude)
        self.env['ir.config_parameter'].sudo().set_param(
            'emp_attendance_map_advance_app.longitude', self.longitude)
        self.env['ir.config_parameter'].sudo().set_param(
            'emp_attendance_map_advance_app.max_attendance_distance',
            self.max_attendance_distance)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    location_restriction = fields.Boolean('Branch Location Restriction',
                                          groups="hr.group_hr_user")

    def attendance_manual(self, next_action, lat, longi, entered_pin=None):
        self.ensure_one()
        res_config = self.env['res.config.settings'].sudo().search([],
                                                                   order="id desc",
                                                                   limit=1)
        location_restriction = self.sudo().location_restriction

        if location_restriction == True:
            if not self.address_id:
                raise ValidationError(_('Please Add work address'))
            partner_id = self.address_id
            if partner_id.partner_latitude == 0 or partner_id.partner_longitude == 0:
                raise ValidationError(
                    _('Please Set the Geolocation'
                      ' of the Work Address : %s address first' % partner_id.name))
            max_distance = float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'emp_attendance_map_advance_app.max_attendance_distance'))
            address_location = (
                partner_id.partner_latitude, partner_id.partner_longitude)
            employee_location = (lat, longi)
            dist = distance.distance(address_location, employee_location).km
            if dist > max_distance:
                raise ValidationError(_(
                    'Please Check In near your Working Address : %s' % partner_id.name))
            # if lat and longi:
            #     co_long = float(res_config.longitude)
            #     co_lat = float(res_config.latitude)
            #     if lat != co_lat or longi != co_long:
            #         raise ValidationError(_('Check In from the working area'))
        can_check_without_pin = not self.env.user.has_group(
            'hr_attendance.group_hr_attendance_use_pin') or (
                                        self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_action(next_action)
        return {'warning': _('Wrong PIN')}
