# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.

{
    'name': 'Multiple Write Off Lines in Register Payments(Advanced) - Writeoff',
    'version': '13.0.0.4',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Multiple Write Off Lines in Register Payments',
    'description': """
Manage multiple write off in customer and supplier payments
===========================================================

This application allows you to add multiple write off into single/batch customer or supplier payments.

    """,
    'website': 'http://www.technaureus.com/',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'depends': ['account'],
    'price': 110,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'data': [
        'views/account_payment_view.xml',
        'views/account_payment.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'css': [],
    'images': ['images/multi_writeoff_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
