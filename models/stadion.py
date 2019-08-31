# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StadionPersebaya(models.Model):
	_name = 'persebaya.stadion'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	active = fields.Boolean(default=True, help="The active field allows you to hide the merchandise without removing it.")
	nama = fields.Char(string="Name",required=True)
	image = fields.Binary(string="Picture")
	pemilik =  fields.Char(string="Owner")
	operator = fields.Char(string="Operator",required=True)
	lokasi = fields.Char(string="Location")
	koordinat = fields.Char(string="GeoLocation")
	dibuka = fields.Char(string="Opening")
	kapasitas = fields.Char(string="Capacity")
	pemakai = fields.Char(string="User")

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.nama or ''
			res.append((s.id, nama))

		return res

	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=80):
		if not args:
			args = []
		if name:
			record = self.search([('nama', operator, name)] + args, limit=limit)
		else:
			record = self.search(args, limit=limit)
		return record.name_get()
