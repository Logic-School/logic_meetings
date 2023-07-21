{
    'name': "Logic Meetings",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/meeting_login_details_view.xml',
        'views/meeting_schedule_details.xml',
    ],
    'demo': [],
    'summary': "Logic Meetings",
    'description': "",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}