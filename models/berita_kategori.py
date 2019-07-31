from odoo import models, fields, api

class PersebayaBeritaKategori(models.Model):
	_name = 'persebaya.berita.kategori'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	name = fields.Char(string="Nama Kategori")
	description = fields.Text(string="Deskripsi")