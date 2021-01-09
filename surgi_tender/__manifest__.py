{
    'name': 'Surgitech Tender Integration',
    'version': '1.1',
    'author': 'Karim Muhammad, Dalia Atef , Zienab Abd EL Nasser',
    'category': 'Integration',
    'website': 'zadsolutions.odoo.com',
    'depends': ['surgi_operation'],
    'data': [
        'security/ir.model.access.csv',
        'security/surgitech_tender_security.xml',
        'views/surgitech_tender.xml',
        'views/view_tender_operations_admin.xml',
        #'views/stock_picking_changes.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
