# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PersebayaClub(models.Model):
	_name = 'persebaya.club'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	active = fields.Boolean(default=True, help="The active field allows you to hide the merchandise without removing it.",track_visibility='onchange')
	nama = fields.Char(string="Club Name", required=True,track_visibility='onchange')
	foto_club = fields.Binary(string="Logo",store=True,track_visibility='onchange')
	julukan = fields.Char(string="Nickname",track_visibility='onchange')
	kota = fields.Char(string="City", required=True,track_visibility='onchange')
	negara = fields.Char(string="Country", required=True,track_visibility='onchange')
	federasi = fields.Char(string="Federation", default="PSSI",track_visibility='onchange')
	tgl_berdiri = fields.Date(string="Established", required=True,track_visibility='onchange')
	stadion = fields.Many2one('persebaya.stadion',string="Home Base", required=True,track_visibility='onchange')
	investor = fields.Char(string="Investor",track_visibility='onchange')
	presiden = fields.Char(string="President ",track_visibility='onchange')
	pelatih = fields.Many2one('hr.employee',string="Head Coach")
	liga_id = fields.Many2one('persebaya.liga',string="League",track_visibility='onchange')
	suporter = fields.Char(string="Supporter",track_visibility='onchange')
	status_team = fields.Selection([
		('ofc', 'Internal'),
		('non', 'External'),
	], string="Status Team", default='non', readonly=True,track_visibility='onchange')
	pemain_ids = fields.One2many('hr.employee','club_id',string="Squads")


	@api.multi
	def action_internal(self):
		self.write({'status_team': 'ofc'})

	@api.multi
	def action_external(self):
		self.write({'status_team': 'non'})

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


	@api.depends('pelatih')
	def _compute_pelatih(self):
		for s in self:
			pelatih_id = s.env['hr.employee'].search([('club_id','=',s.id),('department_id','=',7)])
			s.pelatih = pelatih_id

	@api.model
	def get_summary(self,club_id):
		club_ids = self.env['persebaya.club'].search([('id','=',club_id)])
		vals = []
		for club in club_ids:
			data = {
			'stadion': club.stadion.nama,
			'foto_stadion':club.stadion.image,
			'foto_club': club.foto_club,
			'coach': club.pelatih.name,
			'est': club.tgl_berdiri,
			'city':club.kota,
			'ceo': club.presiden,
			'support':club.suporter,
			'alias': club.julukan
			}
			vals.append(data)
		return vals