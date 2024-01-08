# -*- coding: utf-8 -*-
# Part of emdad. See LICENSE file for full copyright and licensing details.

{
    'name': 'emdadBot',
    'version': '1.2',
    'category': 'Productivity/Discuss',
    'summary': 'Add emdadBot in discussions',
    'website': 'https://www.emdad.com/app/discuss',
    'depends': ['mail'],
    'auto_install': True,
    'installable': True,
    'data': [
        'views/res_users_views.xml',
        'data/mailbot_data.xml',
    ],
    'demo': [
        'data/mailbot_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mail_bot/static/src/scss/emdadbot_style.scss',
        ],
    },
    'license': 'LGPL-3',
}
