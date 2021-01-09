{
    'name': 'Surgitech Product Pack',
    'version': '1.1',
    'category': 'Sales',
    'depends': ['sale','stock'],

    'data': [

        'security/ir.model.access.csv',
        'views/product_changes_view.xml',
        'views/sale_view.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}
