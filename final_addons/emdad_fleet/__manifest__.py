{
    'name': 'Fleet System Emdad',
    'version': '1.0',
    'description': 'Fleet Management for Emdad',
    'summary': 'Fleet Management System',
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'base', 'emdad_inventory', 'emdad_contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_management.xml',
    ],
    # 'demo': [
    #     ''
    # ],
    'auto_install': True,
    'application': False,
    'assets': {
        
    }
}