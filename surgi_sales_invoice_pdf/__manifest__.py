# -*- coding: utf-8 -*-
{
    'name': "Surgi Sales Invoice PDF",

    'summary': """
        Custom Sales Invoice PDF.
    """,

    'description': """
    """,

    'author': "Surgi tech",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'account', 'ehcs_qr_code_invoice', 'surgi_operation'],

    # always loaded
    'data': [
        'views/sales_invoice_report.xml',
        'views/res_company.xml'
    ],
}
