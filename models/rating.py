from odoo import fields, models

class PersebayaPerfomance(models.Model):
	_name = 'persebaya.rating'
	# _inherit = ['mail.thread', 'ir.needaction_mix']

	employee_id = fields.Many2one('hr.employee',string="Employee",readonly=True)
	rating = fields.Integer(string="Rating")
	review = fields.Text(string="Review")