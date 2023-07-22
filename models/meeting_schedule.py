from odoo import fields, api, models
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, time, timedelta,timezone
import pytz
from . import scheduling
class MeetingSchedule(models.Model):
    _name = "meeting.schedule"
    start_time = fields.Float(string="Start Time",required=True,default=0.0)
    end_time = fields.Float(string="End Time",required=True,default=0.0)
    # date_time = fields.Datetime(string="End Time")
    start_date = fields.Date(string="Start Date") 
    subject = fields.Char(string="Subject")
    host = fields.Many2one('res.users',string="Host")
    assigned_id = fields.Many2one('meeting.login', string="Login ID", store=True)
    req_capacity = fields.Integer(string="Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn')])
    schedule_type = fields.Selection([('standard','Standard'),('recurring','Recurring')], string="Meeting Type")
    standard_meet_date = fields.Date(string="Meeting Date")
    dates = fields.One2many('meeting.date','schedule_id', string="Meeting Dates")
    weekdays = fields.Many2many('meeting.weekday',string="Weekdays")
    scheduled = fields.Boolean(string="Is Scheduled")

    def unschedule_meetings(self):
        for record in self:
            record.dates = False
            record.scheduled=False

    def schedule_meetings(self):
        for record in self:
            if record.schedule_type=="standard" and record.standard_meet_date and not record.scheduled:
                # date = datetime.strptime((record.standard_meet_date).strftime('%d '), '%d %b %Y').replace(hour=11, minute=59)
                start_hour,start_minutes = str( round(record.start_time,2)).split('.')
                end_hour,end_minutes = str(record.end_time).split('.')
                start_hour = int(start_hour)
                start_minutes = int( (int(start_minutes)/100) * 60)
                end_hour = int(end_hour)
                end_minutes = int( (int(end_minutes)/100) * 60)

                start_datetime = datetime.combine(record.standard_meet_date, time(hour=start_hour, minute=start_minutes))
                
                # to fix time always starting at +5:30
                start_datetime = start_datetime - timedelta(hours=5,minutes=30)
                
                end_datetime = datetime.combine(record.standard_meet_date, time(hour=end_hour, minute=end_minutes))
                # to fix time always starting at +5:30
                end_datetime = end_datetime - timedelta(hours=5,minutes=30)

                # Add the time from time_field to the datetime object
                # new_start_datetime = start_datetime + timedelta(hours = start_hour, minutes=start_minutes)

                date_obj = self.env['meeting.date'].create({
                    'start_datetime':start_datetime,
                    'end_datetime': end_datetime,
                    'schedule_id': record.id,
                })
                record.dates = date_obj
                record.scheduled = True
                # date_obj = self.env['meeting.date'].

    def get_available_login_id(self):
        for record in self:
            successfully_assigned = scheduling.get_login_id(self,record)
            if not successfully_assigned:
                raise ValidationError("No Login ID's are currently available!")
    def release_login_id(self):
        for record in self:
            if record.assigned_id:
                login_ids = self.env['meeting.login'].search([('meeting_platform','in',(record.meeting_platform,'dual'))])
                for login_id in login_ids:
                    if login_id.current_user == record.host:
                        record.assigned_id = False
                        login_id.write({'current_user': False})
                    elif login_id.second_user == record.host:
                        record.assigned_id = False
                        login_id.write({'second_user': False})


# class Reservations(models.Model):
#     _name="meeting.reservation"
#     login_id = fields.Many2one('meeting.login')
#     timedate = fields.Datetime(string="Time and Date")
#     host1 = fields.Many2one('meeting.login',related="login_id.current_user")
#     host2 = fields.Many2one('meeting.login',related="login_id.second_user")