# -*- coding: utf-8 -*-
{
    'name': "Surgi HR Recruitment",

    'summary': """
        """,

    'description': """
    """,

    'author': "SurgiTech",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment_survey', 'hr_recruitment', 'calendar'],
    'data': [
        'security/access.xml',
        'views/hr_job.xml',
        'views/hr_applicant.xml',
        'views/calendar_event.xml'
    ],
}
