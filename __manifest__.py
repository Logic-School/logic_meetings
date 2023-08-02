{
    'name': "Meetings Scheduler",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/meeting_login_details_view.xml',
        'views/meeting_schedule_details.xml',
        'views/meeting_weekday_view.xml',
        'views/meeting_date_view.xml',
        'data/weekday_data.xml',
    ],
    # 'assets':{
    #     'web.assets_backend': [

    #     ]
    # },
    'demo': [],
    'summary': "Logic Meetings",
    'description': "",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}