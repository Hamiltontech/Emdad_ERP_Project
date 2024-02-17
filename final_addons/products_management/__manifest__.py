{
    'name': 'Products Management System',
    'version': '1.3',
    'website': 'https://www.emdadplatform.sa',
    'category': 'Services/Project',
    'sequence': 45,
    'summary': 'Organize and plan your projects',
    'depends': ['base', 'web'],
    'data':[
        'views/products_management_views.xml',
        'security/ir.model.access.csv',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'products_management/static/src/js/dashboard.js', 
    #         'products_management/static/src/xml/dashboard.xml',
    #     ],
    # },
}