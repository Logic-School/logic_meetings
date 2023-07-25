from odoo import fields, api, models
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, time, timedelta,timezone
import pytz
from . import scheduling
class MeetingSchedule(models.Model):
    _name = "meeting.schedule"
    name = fields.Char(compute="_compute_name")
    start_time = fields.Float(string="Start Time",required=True,default=0.0)
    end_time = fields.Float(string="End Time",required=True,default=0.0)
    # date_time = fields.Datetime(string="End Time")
    start_date_recurring = fields.Date(string="Recurring Start Date") 
    end_date_recurring = fields.Date(string="Recurring End Date")
    subject = fields.Char(string="Subject")
    host = fields.Many2one('res.users',string="Host")
    assigned_id = fields.Many2one('meeting.login', string="Login ID", store=True)
    req_capacity = fields.Integer(string="Required Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn')], required=True)
    schedule_type = fields.Selection([('standard','Standard'),('recurring','Recurring')], string="Meeting Type")
    
    standard_meet_start_datetime = fields.Datetime(string="Start At", readonly=False, store=True)
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
    scheduled = fields.Boolean(string="Is Scheduled",default=False)
    testf = fields.Char(compute="_comp_test")
    @api.depends('start_time')
    def _comp_test(self):
        for record in self:
            record.testf = ''.join((f'{record.start_time:.2f}').split('.'))

    def clear_dates(self):
        # Display the warning prompt
        for record in self:
            self.env['meeting.date'].search([('schedule_id','=',record.id)]).unlink()
            record.dates=False
            record.scheduled=False
    
    def unschedule_meetings(self):
        for record in self:
            # scheduled_dates = self.env['meeting.date'].search(['schedule_id','=',record.id]).unlink()
            # date_records = self.env['meeting.date'].search(['schedule_id','=',record.id])
            # for date in date_records:
            #     date.write({
            #         'scheduled': False
            #     })
            # record.dates = False
            record.scheduled=False

    def schedule_meetings(self):
        for record in self:
            if record.schedule_type=="standard" and record.standard_meet_start_datetime and record.standard_meet_end_datetime and not record.scheduled:
                # date = datetime.strptime((record.standard_meet_date).strftime('%d '), '%d %b %Y').replace(hour=11, minute=59)
                # start_datetime,end_datetime = scheduling.get_start_end_datetime(record)
                date_obj = self.env['meeting.date'].create({
                    'start_datetime':record.standard_meet_start_datetime,
                    'end_datetime': record.standard_meet_end_datetime,
                    'schedule_id': record.id,
                })
                record.dates = date_obj
                record.scheduled = True
                # date_obj = self.env['meeting.date'].

            if record.schedule_type == "recurring" and record.start_date_recurring and record.end_date_recurring:
                start_datetime,end_datetime,time_difference = scheduling.get_start_end_datetime(record,start_date=record.start_date_recurring, end_date=record.end_date_recurring)
                dates = scheduling.get_all_dates_in_a_period(time_difference,start_datetime,end_datetime,weekdays=scheduling.get_weekdays(record))
                for date in dates:
                    date_obj = self.env['meeting.date'].create({
                        'start_datetime':date[0],
                        'end_datetime':date[1],
                        'schedule_id': record.id,
                    })
                record.dates = self.env['meeting.date'].search([('schedule_id','=',record.id)])
                record.scheduled = True
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
                        # record.assigned_id = False
                        login_id.write({'current_user': False})
                    elif login_id.second_user == record.host:
                        # record.assigned_id = False
                        login_id.write({'second_user': False})
                record.assigned_id = False
    def _compute_name(self):
        for record in self:
            name=""
            if record.subject:
                name+=(record.subject).upper()+"-"
            
            if record.meeting_platform=="zoom":
                name+="ZM-"
            elif record.meeting_platform=="elearn":
                name+="ELN-"

            if record.schedule_type=="standard":
                name+="STD"
            elif record.schedule_type=="recurring":
                name+="RCR"   
            
            record.name=name

# class Reservations(models.Model):
#     _name="meeting.reservation"
#     login_id = fields.Many2one('meeting.login')
#     timedate = fields.Datetime(string="Time and Date")
#     host1 = fields.Many2one('meeting.login',related="login_id.current_user")
#     host2 = fields.Many2one('meeting.login',related="login_id.second_user")