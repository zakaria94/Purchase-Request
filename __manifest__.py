# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",
    'summary': """
        Purchase Request Addons
        """,

    'description': """
        Purchase Request Addons
    """,
    'author': "Muhammed Ashraf",
    'website': "http://www.yourcompany.com",
    'category': 'Purchase',
    'version': '13.1',
    'depends': ['purchase'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml',
        'data/mail_template.xml',
        'wizard/purchase_request_reject.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
