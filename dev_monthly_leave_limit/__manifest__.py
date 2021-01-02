# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Leave Monthly Limitation',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
odoo Module add below functionality into odoo

        1.This module helps you to allow monthly leave Limitation on employee leave request
        
        Tags:
        employee leave request
        employee Monthly leave request
        Allow monthly leave Limitation
        Monthly leave limit
        Employee leave Limitation
        Leave Limitation
        odoo Leave Limitation
        Monthly leave limit in odoo
        Leave Monthly Limitation in odoo
Leave Monthly Limitation
Odoo Leave Monthly Limitation
Leave limitation
Odoo leave limitation
HR leave limitation
Odoo HR leave limitation
Monthly leave limitation
Odoo monthly leave limitation
Leave request
Odoo leave request
Monthly leave request
Odoo monthly leave request
Leave limitation on employee leave
Odoo leave limitation on employee leave 
Monthly leave limit
Odoo monthly leave limit
Set monthly leave limit
Odoo set monthly leave limit
HR leave 
Odoo HR Leave


    """,
    'summary': 'odoo app allow monthly leave Limitation on employee leave request on specific leave type',
    'depends': ['hr_holidays'],
    'data': [
        'views/hr_leave_type_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':29.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',  
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
