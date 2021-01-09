# -*- coding: utf-8 -*-
{
    'name': "surgi_hr_employee",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "SURGI-TECH",
    'website': "http://www.surgitech.net",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll'],

    # always loaded
    'data': [
        ## 'views/eg_hr_payroll_report_templates.xml',
        'views/hr_employee_changes.xml',
        'views/hr_department_changes.xml',
        'data/surgi_hr_employee_data.xml',
        'views/hr_employee.xml',
        # 'views/print_employee_badge.xml',
        # 'report/eg_hr_payroll_report.xml',
        # #'views/education_degree_view.xml',
    ],
}