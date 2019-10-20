# -*- coding: utf-8 -*-

from odoo import fields, models,api

class PersebayaPerfomance(models.Model):
	_name = 'persebaya.rating'
	# _inherit = ['mail.thread', 'ir.needaction_mix']

	employee_id = fields.Many2one('hr.employee',string="Name",readonly=True)
	jadwal_id = fields.Many2one('persebaya.jadwal',string="Schedule",readonly=True)
	rating = fields.Integer(string="Rating")
	review = fields.Char(string="Review")

	@api.multi
	def action_remove_review(self):
		self.write({'review':''})

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.employee_id.name or ''
			res.append((s.id, nama))

		return res
