# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StadionPersebaya(models.Model):
	_name = 'persebaya.stadion'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	active = fields.Boolean(default=True, help="The active field allows you to hide the merchandise without removing it.")
	nama = fields.Char(string="Nama Stadion",required=True)
	image = fields.Binary(string="Foto Stadion")
	pemilik =  fields.Char(string="Pemilik Stadion")
	operator = fields.Char(string="Operator Stadion",required=True)
	lokasi = fields.Char(string="Lokasi")
	koordinat = fields.Char(string="GeoLocation")
	dibuka = fields.Char(string="Dibuka pada")
	kapasitas = fields.Char(string="Kapasitas Stadion")
	pemakai = fields.Char(string="Pemakai Stadion")

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
