import requests

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
            'start_time': start_datetime,  # Replace with the desired start time
            'duration': 30,  # Meeting duration in minutes
            'timezone': 'Asia/Calcutta',  # Replace with the desired timezone
            'agenda': record.description,
            # 'use_pmi':True
        }
    else:
        # weekdays = ','.join([str(weekday) for weekday in weekdays])
        data = {
                'topic': record.subject,
                'type': 3,  # 3 for recurring meeting
                'start_time': start_datetime,  # Replace with the desired start time for the first occurrence
                'duration': minutes,  # Meeting duration in minutes
                'timezone': 'Asia/Calcutta',  # Replace with the desired timezone
                'recurrence': {
                    'type': 3,  # 3 for weekly recurrence
                    'repeat_interval': 1,  # Number of weeks between each occurrence
                    'weekly_days': weekdays,  # Comma-separated list of weekday numbers (1: Monday, 5: Friday)
                    'end_date_time': end_datetime,  # Last day of March
                },
                'agenda': record.description,
            }
    response = requests.post(create_meeting_url, headers=headers, json=data)
    if response.status_code==201:
        record.zoom_meeting_link=response.json().get('start_url')
        record.zoom_meet_id=response.json().get('id')
        record.zoom_meet_pass=response.json().get('password')
        
    else:
        record.zoom_meeting_link=False