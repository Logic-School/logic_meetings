from datetime import date

def get_login_id(self,record):
    if not record.assigned_id:
        successfully_assigned=False
        compatible_login_ids = self.env['meeting.login'].search([ '&', ('meeting_platform', 'in', (record.meeting_platform,'dual') ), ('capacity', '>=', record.req_capacity)])
        for login_id in compatible_login_ids:   
            if login_id.meeting_platform=="dual":
                if (not login_id.current_user) or (not login_id.second_user):
                    record.assigned_id = login_id
                    successfully_assigned=True
                    if not login_id.current_user:
                        login_id.write({
                            'current_user': record.host,
                        })
                    elif not login_id.second_user:
                        login_id.write({
                            'second_user' : record.host,
                        })

            else:
                if not login_id.current_user:
                    record.assigned_id = login_id
                    login_id.write({
                        'current_user': record.host,
                    })
                    successfully_assigned=True
                else:
                    record.assigned_id = False
                    login_id.write({
                        'current_user': False
                    })
                    successfully_assigned=True
        return successfully_assigned
    return False
            