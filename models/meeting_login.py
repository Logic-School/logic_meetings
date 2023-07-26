from odoo import models,api,fields
from datetime import datetime

class MeetingHandle(models.Model):
    _name="meeting.login"
    _rec_name = "login_id"
    login_id = fields.Char(string="Login ID", unique=True)
    password = fields.Char(string="Password")
    capacity = fields.Integer(string="Max Capacity")
    meeting_platform = fields.Selection([('zoom','Zoom'),('elearn','ELearn'),('dual','Dual(Zoom and ELearn)')], string="Meeting Platform")
    current_user = fields.Many2one("res.users",string="Current User",compute="_compute_current_second_user")
    second_user = fields.Many2one("res.users", string="Second User", store=True)
    allocated_start = fields.Datetime(string="Allocated Start")
    allocated_end = fields.Datetime(string="Allocated End")
    schedules = fields.One2many('meeting.schedule','assigned_id',string="Schedules")

    def check_if_current_time_slot_occupied(self,date_obj,current_datetime):
        if current_datetime>=date_obj.start_datetime and current_datetime<=date_obj.end_datetime:
            return True
        return False
    
    # def check_if_current_time_slot_occupied_dual(self,record,date_obj,current_datetime):
    #     pass
    
    
    def _compute_current_second_user(self):
        for record in self:
            if record.meeting_platform:
                current_datetime = datetime.now()
                if record.meeting_platform!='dual':
                    record.second_user = False
                    date_objs = self.env['meeting.date'].search([('assigned_id','=',record.id),('scheduled','=',True)])    
                    success=False
                    for date_obj in date_objs:
                        if self.check_if_current_time_slot_occupied(date_obj,current_datetime):
                            record.current_user = date_obj.host
                            success=True
                            break
                    if not success:
                        record.current_user=False
                else:
                    date_objs = self.env['meeting.date'].search([('assigned_id','=',record.id),('scheduled','=',True),('meeting_platform','=','zoom')])
                    success=False
                    for date_obj in date_objs:
                        if self.check_if_current_time_slot_occupied(date_obj,current_datetime):
                            record.current_user = date_obj.host
                            success=True
                            break
                    if not success:
                        record.current_user=False

                    date_objs = self.env['meeting.date'].search([('assigned_id','=',record.id),('scheduled','=',True),('meeting_platform','=','elearn')])
                    for date_obj in date_objs:
                        if self.check_if_current_time_slot_occupied(date_obj,current_datetime):
                            record.second_user = date_obj.host
                            success=True
                            break
                    if not success:
                        record.second_user=False



