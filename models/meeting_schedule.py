from odoo import fields, api, models

class MeetingSchedule(models.Model):
    _name = "meeting.schedule"
    date_time = fields.Datetime(string="Date and Time")
    subject = fields.Char(string="Subject")
    host = fields.Many2one('res.users',string="Host")
    assigned_id = fields.Many2one('meeting.login', string="Login ID", readonly=True, store=True)
    req_capacity = fields.Integer(string="Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn')])

    # def get_available_login_id(self):
    #     for record in self:
    #         compatible_login_ids = self.env['meeting.login'].search([('meeting_platform','=',record.meeting_platform),'|',('meeting_platform','=','dual'),'&',('capacity','<=',record.req_capacity)])

