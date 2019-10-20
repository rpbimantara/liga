# -*- coding: utf-8 -*-

from odoo import models, fields, api

class UkuranPersebaya(models.Model):
	_name = 'persebaya.ukuran'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	kategori_ukuran = fields.Char(string="Kategori Ukuran")
	data_ukuran_line = fields.One2many('persebaya.ukuran.lines','ukuran_id',string="Data Ukuran")

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.kategori_ukuran or ''
			res.append((s.id,nama))

		return res

class UkuranLinesPersebaya(models.Model):
	_name = 'persebaya.ukuran.lines'

	ukuran_id = fields.Many2one('persebaya.ukuran',string="Kategori Ukuran",readonly=True)
	name = fields.Char(string="Ukuran")
	detail_ukuran = fields.Text(string="Detail ukuran", help="Detail Panjang, Lebar, Tinggi, Diameter Ukuran")

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.ukuran_id or ''
			res.append((s.id,nama))

		return res