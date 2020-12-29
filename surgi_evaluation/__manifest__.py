# -*- coding: utf-8 -*-
{
    'name': "surgi_evaluation",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll','surgi_hr_employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/evaluation_groups.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/employee.xml',
        'views/evaluation_direct_subordinate.xml',
        'views/evaluation_sub_direct_subordinate.xml',
        'views/evaluation_indirect_subordinate.xml',
        'views/evaluation_employee_self_assessment.xml',
        'views/config_ratio.xml',
        'views/evaluation_wizard.xml',
        'demo/demo.xml',
        'views/eval_dep.xml',

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
