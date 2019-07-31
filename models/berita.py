# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PersebayaBerita(models.Model):
	_name = 'persebaya.berita'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = "create_date desc"

	title = fields.Char(string="Title")
	headline = fields.Char(string="Headline")
	image = fields.Binary(string="Foto Berita")
	content = fields.Text (string="Konten Berita")
	kategori_brita_id = fields.Many2one('persebaya.berita.kategori',string="Kategori")

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

	name = fields.Char(string="Nama Kategori")
	description = fields.Text(string="Deskripsi")