{
    'name': 'Emdad Procurement',
    'category': 'Sales',
    'description': """
Send KPI Digests periodically
=============================
""",
    'version': '1.1',
    'depends': ['base', 'products_management', 'emdad_inventory', 'web', 'emdad_finance_product'],
    'data': [
        'security/ir.model.access.csv',
        'views/emdad_procurement_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'emdad_procurement/static/src/**/*',
            # 'emdad_procurement/static/src/xml/main_screen.xml',
        ],
    },
}