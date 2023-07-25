from odoo import fields, models, api

class MeetingWeekday(models.Model):

    _name="meeting.weekday"
    _rec_name = 'weekday'   #fields.Char(string="Day", compute="_compute_name")
    weekday = fields.Selection(
        [('monday','Monday'),
        ('tuesday','Tuesday'),
        ('wednesday','Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday',' Sunday')],
        string="Weekday" ,                              
        unique=True   ,
        default="monday",
                                    
        )
    # @api.depends('weekday')
    # def _compute_name(self):
    #     for record in self:
    #         record.name = dict(self._fields['weekday'].selection)[record.weekday]