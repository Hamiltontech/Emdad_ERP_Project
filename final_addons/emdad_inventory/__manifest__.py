{
    'name': 'Emdad Inventory',
    'category': 'Sales',
    'description': """
Send KPI Digests periodically
=============================
""",
    'version': '1.1',
    'depends': ['base', 'products_management'], 
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
