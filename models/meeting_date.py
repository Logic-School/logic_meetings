from odoo import fields, models, api

class MeetingDate(models.Model):
    _name = "meeting.date"
    start_datetime = fields.Datetime(string="Start Datetime")
    end_datetime = fields.Datetime(string="End Datetime")
    schedule_id = fields.Many2one('meeting.schedule',string="Schedule ID")