import requests
from odoo.exceptions import UserError

token_url = 'https://zoom.us/oauth/token'
create_meeting_url = 'https://api.zoom.us/v2/users/me/meetings'
def get_request_data_for_token(zoom_account_id,zoom_client_id,zoom_client_secret):
    data = {
        'grant_type': 'account_credentials',
        'account_id': zoom_account_id,
        'client_id': zoom_client_id,
        'client_secret': zoom_client_secret,
    }
    return data
def get_access_token(zoom_account_id,zoom_client_id,zoom_client_secret):
    data = get_request_data_for_token(zoom_account_id,zoom_client_id,zoom_client_secret)
    response = requests.post(token_url,data=data)
    access_token = response.json().get('access_token')
    return access_token
def create_zoom_meeting(record,access_token,start_datetime,minutes,end_datetime=False,recurring=False,weekdays=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    if not recurring:
        data = {
            'topic': record.subject,
            'type': 2,  # 2 for scheduled meeting, 3 for recurring meeting
            'start_time': start_datetime+'Z',  # Replace with the desired start time
            'duration': minutes,  # Meeting duration in minutes
            # 'timezone': 'Asia/Kolkata',  # Replace with the desired timezone
            'agenda': record.description,
            'use_pmi':True
        }
    else:
        # in datetime object weekday start with monday(0) and ends at sunday(6). in zoom api, weekday start at sunday(1) and ends at saturday(7)
        # if else case is to prevent day from being 1 when it is saturday
        weekdays = ','.join([ str( (weekday+2)%7 ) if weekday!=5  else str(weekday+2) for weekday in weekdays  ])
        data = {
                'topic': record.subject,
                'type': 8,  # 3 for recurring meeting
                'start_time': start_datetime,  # Replace with the desired start time for the first occurrence
                'duration': minutes,  # Meeting duration in minutes
                'timezone': 'Asia/Kolkata',  # Replace with the desired timezone
                'recurrence': {
                    'type': 2, 
                    'repeat_interval': 1,  # Number of weeks between each occurrence
                    'weekly_days': weekdays,  # Comma-separated list of weekday numbers (1: Monday, 5: Friday)
                    'end_date_time': end_datetime+'Z',  # In UTC time
                },
                'agenda': record.description,
            } 
    response = requests.post(create_meeting_url, headers=headers, json=data)
    if response.status_code==201:
        record.zoom_meeting_link=response.json().get('start_url')
        record.zoom_join_link=response.json().get('join_url')
        if recurring:
            record.zoom_meet_id=response.json().get('id')
        else:
            record.zoom_meet_id=response.json().get('pmi')
        record.zoom_meet_pass=response.json().get('password')
        # raise UserError(str(data.keys())+str(data.values()))
    else:
        record.zoom_meeting_link=False
        raise UserError(str(data.keys())+str(data.values()))
    # raise UserError(str(data.keys())+str(data.values()))
