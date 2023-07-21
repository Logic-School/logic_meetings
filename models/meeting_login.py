from odoo import models,api,fields

class MeetingHandle(models.Model):
    _name="meeting.login"
    _rec_name = "login_id"
    login_id = fields.Char(string="Login ID")
    password = fields.Char(string="Password")
    capacity = fields.Integer(string="Max Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn'),('dual','Dual(Zoom and ELearn)')], string="Meeting Platform")
    current_user = fields.Many2one("res.users",string="Current User",readonly=True, store=True)
    second_user = fields.Many2one("res.users", string="Second User", readonly=True, store=True)
