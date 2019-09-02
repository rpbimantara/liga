# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class PersebayaLiga(models.Model):
	_name = 'persebaya.liga'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	nama = fields.Char(string="League", required=True)
	image = fields.Binary(string="Logo")
	negara = fields.Many2one('res.country',string="Country")
	thn_bentuk = fields.Date(string="Start Date")
	jmlh_tim = fields.Integer(string="Teams Participant",compute='_compute_klasemen')
	juara_lalu = fields.Many2one('persebaya.club', string="Last Season", readonly=True)
	klub_sukses = fields.Many2one('persebaya.club', string="Champion", readonly=True)
	website = fields.Char(string="Website")
	klasemen_ids = fields.One2many('persebaya.liga.klasemen','liga_id', string="Standings")
	tgl_validasi = fields.Datetime(string="Validation Date", readonly=True)
	status_liga = fields.Selection([
		('draft', 'DRAFT'),
		('valid', 'VALID'),
	], string="State", default='draft')

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

class PersebayaLigaKlasemen(models.Model):
	_name = 'persebaya.liga.klasemen'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = "point desc"

	liga_id = fields.Many2one('persebaya.liga',string="League")
	club_id = fields.Many2one('persebaya.club',string="Team")
	play = fields.Integer(string="Play",default=0,compute='_compute_klasemen')
	win = fields.Integer(string="Win",default=0,compute='_compute_klasemen')
	draw = fields.Integer(string="Draw",default=0,compute='_compute_klasemen')
	lose = fields.Integer(string="Lose",default=0,compute='_compute_klasemen')
	gm = fields.Integer(string="GF",default=0,compute='_compute_klasemen')
	gk = fields.Integer(string="GA",default=0,compute='_compute_klasemen')
	gd = fields.Integer(string="GD",default=0,compute='_compute_klasemen')
	point = fields.Integer(string="Point",default=0,compute='_compute_klasemen')

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.club_id.nama or ''
			res.append((s.id, nama))

		return res
	
	@api.one
	def _compute_klasemen(self):
		jadwal_ids = self.env['persebaya.jadwal'].search([('liga_id','=',self.liga_id.id),('status_jadwal','=','selesai')])
		gm = 0
		gk = 0
		win = 0
		draw = 0
		lose = 0
		for jadwal in jadwal_ids:
			if jadwal.home.id == self.club_id.id or jadwal.away.id == self.club_id.id:
				self.play += 1
				if jadwal.hasil == 'draw':
					draw += 1
				elif jadwal.hasil == 'home' and jadwal.home.id == self.club_id.id:
					win += 1
					gm += int(jadwal.ft_home)
				elif jadwal.hasil == 'away' and jadwal.away.id == self.club_id.id:
					win += 1
					gm += int(jadwal.ft_away)
				else:
					lose += 1
					gk += int(jadwal.ft_home)
		self.gk = gk
		self.gm = gm
		self.gd = gm - gk
		self.win = win
		self.draw = draw
		self.lose = lose
		self.point = (win * 3) + (draw * 1)


	@api.model
	def klasemen(self,id_liga):
		vals = []
		klasemen_ids = self.env['persebaya.liga.klasemen'].search([('liga_id','=',id_liga)])
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
		# print vals
		return vals