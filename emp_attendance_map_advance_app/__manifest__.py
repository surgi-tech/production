# -*- coding: utf-8 -*-

{
    "name" : "Employee Attendance Location with Restriction",
    "author": "Edge Technologies",
    "version" : "13.0.1.0",
    "live_test_url":'',
    "images":["static/description/main_screenshot.png"],
    'summary': 'Employee Attendance with Google Map Employee Attendance location restriction for employee Attendance google map location of attendance sign in location find location of employee user location sign in location of sign in employee location sign in sign out',
    "description": """
    
    This app helps to track employee login location with google maps and also restrict user check in if location is not matched.
    
    """,
    "license" : "OPL-1",
    "depends" : ['base','web','hr','hr_attendance','emp_attendance_google_map_app'],
    "data": [
        'views/employee_map_attendance_view.xml',
        'views/hr_employee.xml',
        'views/hr_attendance.xml'
    ],
    'external_dependencies' : {
        'python' : ['googlegeocoder','googlemaps' , 'geopy'],
    },
    'qweb': [
        'static/src/xml/attendance.xml',
    ],
    "auto_install": False,
    "installable": True,
    "price": 38,
    "currency": 'EUR',
    "category" : "Website",
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
