# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Leave Before Days Alert",
    
    'author' : 'Softhealer Technologies',

    'website': 'https://www.softhealer.com',    
    
    "support": "info@softhealer.com",   
    
    'version': '12.0.1',
    
    'category': "Human Resources",
    
    'summary': """Leave Before Days Alert,specific leave alert module, leave management app, leave before days alert, notification before leave, leave custom popup, wrong leave warning popup odoo""",

    'description': """Some leaves can be applicable before some specific days. For ex. hajj leave applicable before 15 days. now if some one try to apply leave for hajj before 1 day than it will give error message. so this module restrict user to apply leave before specific time duration. Very easy to configured days in leave type.
	
	specific leave alert module, leave management app, leave before days alert, notification before leave, leave custom popup, wrong leave warning popup odoo
	""",
    "depends": ['hr','hr_holidays'],
    
    "data": [
            'views/hr_leave_days.xml',       
            ],    

    'images': ['static/description/background.png',],             
    
    "installable": True,    
    "application": True,    
    "autoinstall": False,
    
    "price": 20,
    "currency": "EUR"        
}
