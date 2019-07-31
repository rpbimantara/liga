# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class PersebayaLiga(models.Model):
	_name = 'persebaya.liga'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	nama = fields.Char(string="Nama Liga", required=True)
	image = fields.Binary(string="Foto Liga")
	negara = fields.Many2one('res.country',string="Negara")
	thn_bentuk = fields.Date(string="Dibentuk")
	jmlh_tim = fields.Integer(string="Jumlah Tim",compute='_compute_klasemen')
	juara_lalu = fields.Many2one('persebaya.club', string="Juara bertahan", readonly=True)
	klub_sukses = fields.Many2one('persebaya.club', string="Klub Tersukses", readonly=True)
	website = fields.Char(string="Website")
	klasemen_ids = fields.One2many('persebaya.liga.klasemen','liga_id', string="Klasemen")
	tgl_validasi = fields.Datetime(string="Tanggal Validasi", readonly=True)
	status_liga = fields.Selection([
		('draft', 'DRAFT'),
		('valid', 'VALID'),
	], string="Status Liga", default='draft')

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.nama or ''
			res.append((s.id, nama))

		return res

	@api.multi
	def open_list_jadwal(self):
		action = self.env.ref('persebaya.action_show_jadwal')
		result = action.read()[0]
		temp_ids = [stock.id for stock in self.env['persebaya.jadwal'].search([('liga_id','=',self.id)])]
		result['domain'] = [('id', 'in', temp_ids)]
		return result

	@api.multi
	def action_draft(self):
		self.write({'status_liga':'draft'})

	@api.multi
	def action_valid(self):
		for s in self:
			for k in s.klasemen_ids:
				for l in self.env['persebaya.club'].search([]):
					if k.club_id.id == l.id:
						l.liga_id = self.id
		self.write({'status_liga':'valid','tgl_validasi':datetime.now().strftime('%Y-%m-%d')})

	@api.depends('klasemen_ids')
	def _compute_klasemen(self):
		for s in self:
			s.jmlh_tim = len([line for line in s.klasemen_ids])

	def klasemen(self):
		vals = []
		liga_ids = self.env['persebaya.liga'].search([('id','=',10)])
		for klasemen in liga_ids.klasemen_ids:
			data = {
					'id' : klasemen.id,
					'id_club' : klasemen.club_id.id,
					'foto_club' : klasemen.club_id.foto_club,
					'nama_club' : klasemen.club_id.nama,
					'play' : klasemen.play,
					'selisih_gol' : str(klasemen.gm - klasemen.gk),
					'point' : klasemen.point
					}
			vals.append(data)
		return vals

class PersebayaLigaKlasemen(models.Model):
	_name = 'persebaya.liga.klasemen'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	liga_id = fields.Many2one('persebaya.liga',string="Liga")
	club_id = fields.Many2one('persebaya.club',string="Nama Club")
	play = fields.Integer(string="Main",default=0,readonly=True)
	win = fields.Integer(string="Menang",default=0,readonly=True)
	draw = fields.Integer(string="Seri",default=0,readonly=True)
	lose = fields.Integer(string="Kalah",default=0,readonly=True)
	gm = fields.Integer(string="Gol Masuk",default=0,readonly=True)
	gk = fields.Integer(string="Gol Kemasukan",default=0,readonly=True)
	point = fields.Integer(string="Point",default=0,readonly=True)

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.club_id.nama or ''
			res.append((s.id, nama))

		return res


	def klasemen(self):
		vals = []
		klasemen_ids = self.env['persebaya.liga.klasemen'].search([])
		print klasemen_ids
		for klasemen in klasemen_ids:
			data = {
					'id' : klasemen.id,
					'foto_club' : klasemen.club_id.foto_club,
					'nama_club' : klasemen.club_id.nama,
					'play' : klasemen.play,
					'selisih_gol' : str(klasemen.gm - klasemen.gk),
					'point' : klasemen.point
					}
			vals.append(data)
		print vals
		return vals