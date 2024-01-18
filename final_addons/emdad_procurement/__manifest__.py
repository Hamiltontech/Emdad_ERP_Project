{
    'name': 'Emdad Procurement',
    'category': 'Sales',
    'description': """
Send KPI Digests periodically
=============================
""",
    'version': '1.1',
    'depends': ['base', 'products_management', 'emdad_inventory'],
    'data': [
        'security/ir.model.access.csv',
        'views/emdad_procurement_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}