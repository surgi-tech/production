# -*- coding: utf-8 -*-

import json 


from itertools import groupby
from datetime import datetime, timedelta
import googlemaps
from googlegeocoder import GoogleGeocoder
from geopy.geocoders import Nominatim
from odoo import api, fields, http, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp
from werkzeug.exceptions import NotFound, Forbidden
from odoo.http import request

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object


class SearchResult(http.Controller):

    @http.route(['/google/address'], type='http', auth='public', website=True)
    def google_address(self , **post):
        res_config= request.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        script_key = res_config.google_api_key
        data = []
        if ('lat' or 'long') in post:
            lati = post['lat']
            longti = post['long']
            geocoder = GoogleGeocoder(str(script_key))
            geolocator = Nominatim(user_agent=str(script_key))
            # reverse = geocoder.get((lati, longti))
            reverse = geolocator.reverse((lati, longti))
            try:
                data.append(str(reverse[0]))
                if ('emp' and 'attend') in post:
                    attendance_id = request.env['hr.attendance'].sudo().search([('id','=',int(post['attend'])),('employee_id','=',int(post['emp']))],limit=1)
                    attendance_id.write({
                        'address' : str(reverse[0]),
                        'browser' : str(post['browser']),
                        'os' :  str(post['os'])
                    })
            except IndexError:
                return json.dumps([])
        return json.dumps(data)

    @http.route(['/mylocation/address'], type='json', auth='public', website=True)
    def load_my_map(self , **post):
        res_config= request.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        script_key = res_config.google_api_key
        attendance_ids = request.env['hr.attendance'].sudo().search([('employee_id','=',int(post['emp']))], order='id desc')
        for attendance_id in attendance_ids:
            date = attendance_id.check_in.date()
            date = datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT)
            if post.get('date') != '':
                new_date = post['date']  
                new_date = datetime.strptime(post['date'], DEFAULT_SERVER_DATE_FORMAT)
                if date == new_date:
                    try:
                        address = attendance_id.address
                        gmaps = googlemaps.Client(key=str(script_key))
                        # geocode_result = gmaps.geocode(address)
                        geolocator = Nominatim(user_agent=str(gmaps))
                        geocode_result = geolocator.geocode(address)
                        # latitude = geocode_result[0]['geometry']['location']['lat']
                        # longitude = geocode_result[0]['geometry']['location']['lng']
                        latitude = geocode_result.latitude
                        longitude = geocode_result.longitude
                        final_val = {}
                        data = {}
                        if attendance_id.employee_id.image:
                            src = '/web/image/hr.employee/'+ str(attendance_id.employee_id.id) +'/image'
                        else:
                            src = ''
                        final_val.update({
                            'latitude' : latitude or False,
                            'longitude' : longitude or False ,
                            'map_zoom' : 16,
                            'map_type' : 'roadmap',
                            'map_search_radius' : 5000,
                            'employee' : attendance_id.employee_id.name or '',
                            'image' : src,
                            'date' : new_date or False
                        })
                        data.update({
                            'map_init' :final_val,
                            })
                        return json.dumps(data, cls=DateTimeEncoder)
                    except googlemaps.exceptions.ApiError as e:
                        raise UserError(_('Provided Google APi key Is not Valid !!'))

                else:
                    data = {}
                    return json.dumps(data)
            else:
                raise UserError(_('Mention Date to Find that day Location'))

    @http.route(['/myattendance'], type='json', auth='public', website=True)
    def load_attendance(self , **post):
        data = []
        if 'emp' in post:
            attendance_ids = request.env['hr.attendance'].sudo().search([('employee_id','=',int(post['emp']))],limit=1, order='id desc')
            for attendance_id in attendance_ids:
                date = attendance_id.check_in.date()
                date = datetime.strptime(str(date), DEFAULT_SERVER_DATE_FORMAT)
                new_date = post['date']  
                new_date = datetime.strptime(post['date'], DEFAULT_SERVER_DATE_FORMAT)
                if date == new_date:
                    data.append(attendance_id.id)
        return data

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_api_key = fields.Char(string='API Key', required=True, default='Define API key')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        google_api_key = self.env['ir.config_parameter'].sudo().get_param('emp_attendance_google_map_app.google_api_key')
        res.update(
            google_api_key = google_api_key,
        )
        return res


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('emp_attendance_google_map_app.google_api_key', self.google_api_key)


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    address = fields.Text('Login Location', readonly=True)
    browser = fields.Char('Browser', readonly=True)
    os = fields.Char('OS Details', readonly=True)


class MapView(models.Model):
    _name = 'odoo.map'
    _description = 'Odoo Map View'
    _rec_name = 'employee_id'


    @api.depends('employee_id','date','department_id')
    def _map_key(self):
        if self.employee_id or self.date or self.department_id:
            attendance_id = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)],limit=1,order='id desc')
            res_config= request.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
            if res_config:
                if attendance_id:
                    self.map_key = 'https://maps.googleapis.com/maps/api/js?key=' + res_config.google_api_key
                else:
                    self.map_key = ''
            else:
                self.map_key = ''

    def search_map(self):
        if not self.employee_id:
            raise UserError(_('Mention Employee to Find his/her location.'))
        if not self.date:
            raise UserError(_('Mention Date to Find that day Location'))
        return True

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )

    date = fields.Date(
        string='Date'
    )
    
    map_key = fields.Char(
        string='Map Key', compute='_map_key' , store= True
    )

