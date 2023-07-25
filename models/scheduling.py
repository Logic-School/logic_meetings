from datetime import date,timedelta,time,datetime

# def get_login_id(self,record):
    # if not record.assigned_id:
    #     successfully_assigned=False
    #     compatible_login_ids = self.env['meeting.login'].search([ '&', ('meeting_platform', 'in', (record.meeting_platform,'dual') ), ('capacity', '>=', record.req_capacity)])
    #     for login_id in compatible_login_ids:   
    #         if login_id.meeting_platform=="dual":
    #             if (not login_id.current_user) or (not login_id.second_user):
    #                 record.assigned_id = login_id
    #                 successfully_assigned=True
    #                 if not login_id.current_user:
    #                     login_id.write({
    #                         'current_user': record.host,
    #                     })
    #                 elif not login_id.second_user:
    #                     login_id.write({
    #                         'second_user' : record.host,
    #                     })

    #         else:
    #             if not login_id.current_user:
    #                 record.assigned_id = login_id
    #                 login_id.write({
    #                     'current_user': record.host,
    #                 })
    #                 successfully_assigned=True
    #             else:
    #                 record.assigned_id = False
    #                 login_id.write({
    #                     'current_user': False
    #                 })
    #                 successfully_assigned=True
    #     return successfully_assigned
    # return False

def get_login_id(self,record):
    if not record.assigned_id:
        successfully_assigned=False
        compatible_login_ids = self.env['meeting.login'].search([ '&', ('meeting_platform', 'in', (record.meeting_platform,'dual') ), ('capacity', '>=', record.req_capacity)])
        if record.schedule_type=='standard':
            for login_id in compatible_login_ids:
                if get_suitable_id_standard(record,login_id):
                    record.assigned_id = login_id.id
                    return True
            return False
        elif record.schedule_type=='recurring':
            for login_id in compatible_login_ids:
                available_count = 0
                for date in record.dates:
                    if get_suitable_id_recurring(record,login_id,date):
                        available_count+=1
                    else:
                        break
                if available_count==len(record.dates):
                    record.assigned_id = login_id
                    return True
            return False

# function to check if the required date and time slot is available in a schedule obj 
def check_slot_available(date,rec_start_datetime,rec_end_datetime):
    # if date.start_datetime.date() == record.standard_meet_start_datetime.date():
    # case1 = (date.start_datetime<rec_start_datetime) and (date.end_datetime>rec_start_datetime and date.end_datetime<rec_end_datetime)
    # # case1 = (date.start_datetime<rec_start_datetime) and (date.end_datetime>rec_start_datetime and date.end_datetime>rec_end_datetime)

    # case2 = (date.start_datetime>rec_start_datetime) and (date.start_datetime<rec_end_datetime and date.end_datetime>rec_end_datetime)
    # case3 = (date.start_datetime<rec_start_datetime) and (date.end_datetime>rec_end_datetime)
    # case4 = (date.start_datetime>rec_start_datetime) and (date.end_datetime<rec_end_datetime)
    case1 = (date.start_datetime<rec_start_datetime) and (date.end_datetime<rec_end_datetime) and (date.end_datetime>rec_end_datetime)
    case2 = (date.start_datetime>rec_start_datetime) and (date.end_datetime<rec_end_datetime)
    case3 = (date.start_datetime>rec_start_datetime) and (date.start_datetime<rec_end_datetime) and (date.end_datetime>rec_end_datetime)
    case4 = (date.start_datetime<rec_start_datetime) and (date.end_datetime>rec_end_datetime)
    
    if case1 or case2 or case3 or case4:
        return False
    return True
    

def get_suitable_id_standard(record,login_id):
    if len(login_id.schedules)==0:
        record.assigned_id = login_id.id
        return True
    for schedule in login_id.schedules:
        for date in schedule.dates:
            if date.start_datetime.date() == record.standard_meet_start_datetime.date():
                if not check_slot_available(date,record.standard_meet_start_datetime,record.standard_meet_end_datetime):
                    # record.assigned_id = login_id.id
                    return False
                else:
                    continue
    return True

def get_suitable_id_recurring(record,login_id,recurring_datetime):
    if len(login_id.schedules)==0:
        record.assigned_id = login_id.id
        return True
    for schedule in login_id.schedules:
        for date in schedule.dates:
            if date.start_datetime.date() == recurring_datetime.start_datetime.date():
                if not check_slot_available(date,recurring_datetime.start_datetime,recurring_datetime.end_datetime):
                    return False
    return True

def get_start_end_datetime(record,start_date=None,end_date=None):
    # have to round the time to 2 decimal places before splitting hour and minutes
    start_hour,start_minutes = f'{record.start_time:.2f}'.split('.')
    end_hour,end_minutes = f'{record.end_time:.2f}'.split('.')
    start_hour = int(start_hour)
    # minutes are stored as percentages of an hour. so it has to be converted into actual minutes
    start_minutes = int( (int(start_minutes)/100)*60)
    end_hour = int(end_hour)
    end_minutes = int( (int(end_minutes)/100)*60)

    time_difference = ((end_hour*60) + end_minutes) - ((start_hour*60) + start_minutes)
    # if not start_date and not end_date:
    #     start_datetime = datetime.combine(record.standard_meet_date, time(hour=start_hour, minute=start_minutes))
    #     # to fix time always starting at +5:30
    #     start_datetime = start_datetime - timedelta(hours=5,minutes=30)      
        
    #     end_datetime = datetime.combine(record.standard_meet_date, time(hour=end_hour, minute=end_minutes))
    #     # to fix time always starting at +5:30
    #     end_datetime = end_datetime - timedelta(hours=5,minutes=30)
    #     return start_datetime,end_datetime,time_difference
    
    if start_date and end_date:
        start_datetime = datetime.combine(start_date, time(hour=start_hour, minute=start_minutes))
        # to fix time always starting at +5:30
        start_datetime = start_datetime - timedelta(hours=5,minutes=30)      
        
        end_datetime = datetime.combine(end_date, time(hour=end_hour, minute=end_minutes))
        # to fix time always starting at +5:30
        end_datetime = end_datetime - timedelta(hours=5,minutes=30)
        return start_datetime,end_datetime,time_difference

def get_all_dates_in_a_period(time_difference,start_datetime,end_datetime,weekdays):
    current_date = start_datetime
    dates = []
    # start datetime is stored in index 0
    # end datetime is stored in index 1
    time_difference_obj = (start_datetime+timedelta(minutes=time_difference)) - start_datetime 
    while(current_date<=end_datetime):
        if current_date.weekday() in weekdays:
            start_end_datetimes = []
            start_end_datetimes.append(current_date)
            start_end_datetimes.append(current_date+time_difference_obj)
            dates.append(start_end_datetimes)
        current_date+= timedelta(days=1)
    return dates
            
def get_weekdays(record):
    weekdays = []
    for day in record.weekdays:
        if day.weekday=="monday": weekdays.append(0)
        elif day.weekday=="tuesday": weekdays.append(1)
        elif day.weekday=="wednesday": weekdays.append(2)
        elif day.weekday=="thursday": weekdays.append(3)
        elif day.weekday=="friday": weekdays.append(4)
        elif day.weekday=="saturday": weekdays.append(5)
        elif day.weekday=="sunday": weekdays.append(6)

    return weekdays