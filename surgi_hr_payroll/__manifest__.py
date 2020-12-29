# -*- coding: utf-8 -*-
{
    'name': 'SURGI-TECH Payroll',
    'version': '0.1',
    'category': 'Localization',
    'author': 'SURGI-TECH',

    'website': "www.surgitech.net",
    'depends': ['base','hr', 'hr_payroll','hr_contract','hr_holidays','hr'],


    'description': """

      
    """,

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        #"data/eg_hr_payroll_data.xml",
        'views/hr_grade_rank_view.xml',
        'views/views.xml',
    ],

    'license': 'OPL-1',
}
