{
    'name': 'SURGI-TECH In-Out Inv. Validation Restriction',
    'version': '1.1',
    'category': 'other',
    'description': 'Validate Restriction for In-Out Inventory Transactions '"""
Warehouse Security
==========================
    """,
    'website': 'https://www.surgitech.net',
    'depends': ['stock'],
    'data': [

        'views/stock_picking_changes_view.xml',
        'security/stock_inventory_validate_in_out.xml',
    ],
}
