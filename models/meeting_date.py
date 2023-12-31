from odoo import fields, models, api

class MeetingDate(models.Model):
    _name = "meeting.date"
    _rec_name='subject'
    # _inherit = "mail.activity.mixin"
    start_datetime = fields.Datetime(string="Start Datetime",readonly=True)
    end_datetime = fields.Datetime(string="End Datetime",readonly=True)
    schedule_id = fields.Many2one('meeting.schedule',string="Schedule ID",ondelete="cascade",readonly=True)
    subject = fields.Char(related="schedule_id.subject", store=True)
    scheduled = fields.Boolean(string="Is Scheduled", store=True)
    assigned_id = fields.Many2one('meeting.login',related="schedule_id.assigned_id", string="Assigned ID", store=True)
    host = fields.Many2one('res.users',related="schedule_id.host",string="Host", store=True)
    meeting_platform = fields.Selection(related="schedule_id.meeting_platform",string="Meeting Platform", store=True)

    # def _compute_name(self):
    #     for record in self:
