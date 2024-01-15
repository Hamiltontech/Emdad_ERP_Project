{
    'name': 'Emdad Contacts',
    'category': 'Sales',
    'description': """
Send KPI Digests periodically
=============================
""",
    'version': '1.1',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/emdad_contacts_view.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}