# -*- coding: utf-8 -*-

{
    "name" : "Employee Attendance Location with Google Map",
    "author": "Edge Technologies",
    "version" : "13.0.1.1",
    "images":["static/description/main_screenshot.png"],
    'summary': 'Apps helps Employee Attendance with Google Map Employee Attendance with Map employee location employee google map location of attendance sign in location find location of employee user location sign in location of sign in employee location sign in sign out',
    "description": """
    
    This app helps to track employee login location with google maps.
Odoo 12 Employee Attendance Map
employee loction attendance location employee map location employee google map location of attendance Store Employee Attendance details
check in location employee check in location employee store location check employee location find location of employee check location of employee employee location sales team location user location check in location location of sign in  

    
    """,
    "license" : "OPL-1",
    "depends" : ['base','web','hr','hr_attendance'],
    "data": [
        'security/ir.model.access.csv',
        'views/employee_map_attendance_view.xml',
    ],
    'external_dependencies' : {
        'python' : ['googlegeocoder','googlemaps', 'geopy'],
    },
    'qweb': [
        'static/src/xml/my_attendances_extend_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": 'EUR',
    "category" : "Website",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
