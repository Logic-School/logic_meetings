from odoo import fields, api, models
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, time, timedelta,timezone
import pytz
from . import scheduling
from . import zoom_meetings
class MeetingSchedule(models.Model):
    _name = "meeting.schedule"
    name = fields.Char(compute="_compute_name")
    start_time = fields.Float(string="Start Time",required=True,default=0.0)
    end_time = fields.Float(string="End Time",required=True,default=0.0)
    # date_time = fields.Datetime(string="End Time")
    start_date_recurring = fields.Date(string="Recurring Start Date") 
    end_date_recurring = fields.Date(string="Recurring End Date")
    description = fields.Text(string="Description")
    subject = fields.Char(string="Subject")
    # host = fields.Many2one('res.users',string="Host")
    def _get_default_host(self):
        return self.env.user
    def _compute_is_admin(self):
        for record in self:
            record.is_admin= self.env.user.has_group('logic_meetings.group_meeting_administrator')
    is_admin = fields.Boolean(compute="_compute_is_admin")
    host = fields.Many2one('res.users',string="Host",default=_get_default_host)
    assigned_id = fields.Many2one('meeting.login', string="Login ID", store=True, readonly=True)
    req_capacity = fields.Integer(string="Required Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn')], required=True)
    schedule_type = fields.Selection([('standard','Standard'),('recurring','Recurring')], string="Meeting Type")
    standard_meet_start_datetime = fields.Datetime(string="Start At", readonly=False, store=True)
    testf = fields.Integer(string="Testd")
    schedule_date_view = fields.Char(string="Date",compute="_compute_date_view")
    schedule_start_time_view = fields.Char(string="Start Time", compute="_compute_start_time_view")
    schedule_end_time_view = fields.Char(string="End Time", compute="_compute_end_time_view")
    zoom_meeting_link = fields.Text(string="Meeting Link",default=False)
    zoom_meet_id = fields.Char(string="Meeting ID")
    zoom_meet_pass = fields.Char(string="Meeting Passcode")
    def _compute_start_time_view(self):
        for record in self:
            if record.schedule_type=='standard' and record.standard_meet_start_datetime:
                time_with_ist_diff_added  = record.standard_meet_start_datetime + timedelta(hours=5,minutes=30)
                record.schedule_start_time_view = str(time_with_ist_diff_added.strftime("%H:%M"))
            elif record.schedule_type=='recurring' and record.start_time:
                start_hour,start_minutes = f'{record.start_time:.2f}'.split('.')
                    # minutes are stored as percentages of an hour. so it has to be converted into actual minutes
                start_minutes = str(int( (int(start_minutes)/100)*60))
                # record.schedule_start_time_view = str(start_minutes)
                if int(start_minutes)<10:
                    start_minutes = '0'+start_minutes
                if int(start_hour)<10:
                    start_hour = '0'+start_hour
                record.schedule_start_time_view = start_hour + ":" + start_minutes
            else:
                record.schedule_start_time_view = ""
    
    def _compute_end_time_view(self):
        for record in self:
            if record.schedule_type=='standard' and record.standard_meet_end_datetime:
                time_with_ist_diff_added  = record.standard_meet_end_datetime + timedelta(hours=5,minutes=30)
                record.schedule_end_time_view = str(time_with_ist_diff_added.strftime("%H:%M"))
            elif record.schedule_type=='recurring' and record.end_time:
                start_hour,start_minutes = f'{record.end_time:.2f}'.split('.')
                    # minutes are stored as percentages of an hour. so it has to be converted into actual minutes
                start_minutes = str(int( (int(start_minutes)/100)*60))
                if int(start_minutes)<10:
                    start_minutes = '0'+start_minutes
                if int(start_hour)<10:
                    start_hour = '0'+start_hour
                record.schedule_end_time_view = start_hour + ":" + start_minutes
            else:
                record.schedule_end_time_view = ""
    def _compute_date_view(self):
        for record in self:
            if record.schedule_type=='standard' and record.standard_meet_start_datetime and record.standard_meet_end_datetime:
                record.schedule_date_view = str(record.standard_meet_start_datetime.date())+" to "+str(record.standard_meet_end_datetime.date())
            elif record.schedule_type=='recurring' and record.start_date_recurring and record.end_date_recurring:
                record.schedule_date_view = str(record.start_date_recurring)+" to "+str(record.end_date_recurring)
            else:
                record.schedule_date_view = ""
    # method to set seconds to 0
    @api.onchange('standard_meet_start_datetime')
    def _change_std_start_datetime(self):
        for record in self:
            if record.standard_meet_start_datetime:
                record.standard_meet_start_datetime = record.standard_meet_start_datetime.replace(second=0)
            
    standard_meet_end_datetime = fields.Datetime(string="End At")
    # method to set seconds to 0
    @api.onchange('standard_meet_end_datetime')
    def _change_std_end_datetime(self):
        for record in self:
            if record.standard_meet_start_datetime:
                record.standard_meet_end_datetime = record.standard_meet_end_datetime.replace(second=0)
    
    dates = fields.One2many('meeting.date','schedule_id', string="Meeting Dates")
    weekdays = fields.Many2many('meeting.weekday',string="Weekdays")
    scheduled = fields.Boolean(string="Is Scheduled",compute="_compute_scheduled",store=True)

    @api.depends('dates')
    def _compute_scheduled(self):
        for record in self:
            any_scheduled=False
            for date in record.dates:
                if date.scheduled:
                    any_scheduled=True
                    break
            record.scheduled = any_scheduled 

    def create_zoom_meeting(self):
        for record in self:
            if record.meeting_platform=='zoom' and record.assigned_id:
                access_token = zoom_meetings.get_access_token(record.assigned_id.zoom_account_id,record.assigned_id.zoom_client_id,record.assigned_id.zoom_client_secret)
                if record.schedule_type=='standard':
                    # start_datetime = record.standard_meet_start_datetime
                    # end_datetime = record.standard_meet_end_datetime
                    start_datetime=str(record.standard_meet_start_datetime.date())+"T"+str(record.standard_meet_start_datetime.strftime("%H:%M:%S"))
                    end_datetime=str(record.standard_meet_end_datetime.date())+"T"+str(record.standard_meet_end_datetime.strftime("%H:%M:%S"))
                    # meeting_minutes = (end_datetime - start_datetime).seconds//60
                    meeting_minutes = (record.standard_meet_end_datetime - record.standard_meet_start_datetime).seconds//60
                    zoom_meetings.create_zoom_meeting(record,access_token,start_datetime,meeting_minutes,end_datetime)
                elif record.schedule_type=='recurring':
                    start_datetime=str(record.start_date_recurring)+"T"+record.schedule_start_time_view+":00"
                    end_datetime=str(record.end_date_recurring)+"T"+record.schedule_start_time_view+":00"
                    # start_hour,start_minutes = record.schedule_start_time_view.split(':')
                    # end_hour,end_minutes = record.schedule_end_time_view.split(':')
                    # minutes = (end_hour*60 + end_minutes) -
                    meeting_minutes =  int( (record.end_time*60) - (record.start_time*60) )
                    weekdays = scheduling.get_weekdays(record)
                    zoom_meetings.create_zoom_meeting(record,access_token,start_datetime,meeting_minutes,end_datetime=end_datetime,recurring=True,weekdays=weekdays)
    def start_zoom_meeting(self):
        for record in self:
            return {
                'type': 'ir.actions.act_url',
                'url': record.zoom_meeting_link,
                'target': 'new',
            }
    def clear_dates(self):
        # Display the warning prompt
        for record in self:
            self.env['meeting.date'].search([('schedule_id','=',record.id)]).unlink()
            record.dates=False
            record.scheduled=False
    
    def unschedule_meetings(self):
        for record in self:
            for date in record.dates:
                date.write({
                    'scheduled':False
                })
            record.scheduled=False

    def schedule_meetings(self):
        for record in self:
            if record.schedule_type=="standard" and record.standard_meet_start_datetime and record.standard_meet_end_datetime and not record.scheduled:
                # date = datetime.strptime((record.standard_meet_date).strftime('%d '), '%d %b %Y').replace(hour=11, minute=59)
                # start_datetime,end_datetime = scheduling.get_start_end_datetime(record)
                date_obj = self.env['meeting.date'].create({
                    'start_datetime':record.standard_meet_start_datetime,
                    'end_datetime': record.standard_meet_end_datetime,
                    'scheduled': True,
                    'schedule_id': record.id,
                })
                record.dates = date_obj
                record.scheduled = True
                # date_obj = self.env['meeting.date'].

            elif record.schedule_type == "recurring" and record.start_date_recurring and record.end_date_recurring:
                start_datetime,end_datetime,time_difference = scheduling.get_start_end_datetime(record,start_date=record.start_date_recurring, end_date=record.end_date_recurring)
                if not record.dates:
                    dates = scheduling.get_all_dates_in_a_period(time_difference,start_datetime,end_datetime,weekdays=scheduling.get_weekdays(record))
                    for date in dates:
                        date_obj = self.env['meeting.date'].create({
                            'start_datetime':date[0],
                            'end_datetime':date[1],
                            'scheduled': True,
                            'schedule_id': record.id,
                        })
                    record.dates = self.env['meeting.date'].search([('schedule_id','=',record.id)])
                else:
                    for date in record.dates:
                        date.write({
                            'scheduled':True,
                        })
                record.scheduled = True
            else:
                raise UserError("Make sure all the fields are properly filled before scheduling a meeting!")
    def get_available_login_id(self):
        for record in self:
            successfully_assigned = scheduling.get_login_id(self,record)
            if not successfully_assigned:
                raise ValidationError("Currently all compatible Login IDs for this meeting are scheduled for other meetings!. You could try again after reducing the required capacity or changing the meeting platform")
    def release_login_id(self):
        for record in self:
            if record.assigned_id:
                login_ids = self.env['meeting.login'].search([('meeting_platform','in',(record.meeting_platform,'dual'))])
                for login_id in login_ids:
                    if login_id.current_user == record.host:
                        # record.assigned_id = False
                        login_id.write({'current_user': False})
                    elif login_id.second_user == record.host:
                        # record.assigned_id = False
                        login_id.write({'second_user': False})
                record.assigned_id = False
                record.zoom_meeting_link=False
                record.zoom_meet_id=False
                record.zoom_meet_pass=False
    def _compute_name(self):
        for record in self:
            name=""
            if record.subject:
                name+=(record.subject).upper()+"-"
            
            if record.meeting_platform=="zoom":
                name+="ZOOM "
            elif record.meeting_platform=="elearn":
                name+="ELEARN " 

            if record.schedule_type=='standard' and record.standard_meet_start_datetime:
                name+=str(record.standard_meet_start_datetime.date())
            elif record.schedule_type=='recurring':
                name+=str(record.start_date_recurring) + " to " + str(record.start_date_recurring)
            record.name=name

# class Reservations(models.Model):
#     _name="meeting.reservation"
#     login_id = fields.Many2one('meeting.login')
#     timedate = fields.Datetime(string="Time and Date")
#     host1 = fields.Many2one('meeting.login',related="login_id.current_user")
#     host2 = fields.Many2one('meeting.login',related="login_id.second_user")