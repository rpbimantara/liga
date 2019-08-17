from odoo import fields, models

class PersebayaPerfomance(models.Model):
	_name = 'persebaya.rating'
	# _inherit = ['mail.thread', 'ir.needaction_mix']

	employee_id = fields.Many2one('hr.employee',string="Name",readonly=True)
	jadwal_id = fields.Many2one('persebaya.jadwal',string="Jadwal",readonly=True)
	rating = fields.Integer(string="Rating")
	review = fields.Char(string="Review")