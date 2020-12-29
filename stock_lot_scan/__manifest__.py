{
    'name': 'Stock Lot Scan',
    'version': '1.1',
    'category': 'Sales',
    'website': 'www.surgitech.net',
    'depends': ['stock', 'stock_account', 'sale', 'product','surgi_operation'],#,'bi_picking_analytic'
    'data': [

        # 'views/sale_order_changes_view.xml',

        'views/stock_picking_changes_view.xml',
        'wizard/validation_confirmation_wizard.xml',

        'security/ir.model.access.csv',

    ],
'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

}
