{
    'name': 'Emdad Sales System',
    'version': '1.0',
    'description': '',
    'summary': '',
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'base', 'emdad_inventory','emdad_contacts', 'emdad_finance_product'
    ],
    'data': [
        'views/sales_order_view.xml',
        'security/ir.model.access.csv',
        'reports/delivery_note.xml',
        'reports/delivery_note_action.xml'
    ],
    'installable': True,
    'auto_install': True,
    'demo': [
        ''
    ],
    'application': False,
    'assets': {
        
    }
}