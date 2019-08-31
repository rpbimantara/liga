# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PersebayaBerita(models.Model):
	_name = 'persebaya.berita'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = "create_date desc"

	title = fields.Char(string="Title")
	headline = fields.Char(string="Headline")
	image = fields.Binary(string="Picture")
	content = fields.Text (string="Content")
	kategori_brita_id = fields.Many2one('persebaya.berita.kategori',string="Category")

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			headline = s.headline or ''
			res.append((s.id, headline))

		return res

class PersebayaBeritaKategori(models.Model):
	_name = 'persebaya.berita.kategori'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	name = fields.Char(string="Name")
	description = fields.Text(string="Description")