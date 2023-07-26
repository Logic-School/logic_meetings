from odoo import fields, models, api

class MeetingDate(models.Model):
    _name = "meeting.date"
    _rec_name='subject'
    start_datetime = fields.Datetime(string="Start Datetime")
    end_datetime = fields.Datetime(string="End Datetime")
    schedule_id = fields.Many2one('meeting.schedule',string="Schedule ID",ondelete="cascade")
    subject = fields.Char(related="schedule_id.subject")
    scheduled = fields.Boolean(string="Is Scheduled")
    assigned_id = fields.Many2one('meeting.login',related="schedule_id.assigned_id", string="Assigned ID")
    host = fields.Many2one('res.users',related="schedule_id.host",string="Host")
    meeting_platform = fields.Selection(related="schedule_id.meeting_platform",string="Meeting Platform")

    # def _compute_name(self):
    #     for record in self:
