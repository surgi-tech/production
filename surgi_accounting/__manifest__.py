# -*- coding: utf-8 -*-
{
    'name': "surgi_accounting",

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
    'depends': ['base','hr','hr_contract','hr_payroll_account','stock_account','stock','account','surgi_inventory_changes'],
# 'account','account_accountant','hr','hr_contract','hr_payroll_account','stock_account','stock',
# 'surgi_inventory_changes'

    # always loaded
    'data': [
        'security/accounting_groups.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/inhertit_views.xml',
        'views/account_payment_register.xml',
        'views/account_bank_statement.xml',
        'views/register_payment.xml',
        'views/stock_quant_change_accounting_view.xml',
        'views/payment_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
