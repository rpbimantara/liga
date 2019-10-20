# -*- coding: utf-8 -*-

from odoo import fields, models,api

class HrEmployeeInherit(models.Model):
	_inherit = 'hr.employee'

	tekel_sukses = fields.Integer(string="Tackles",compute='_compute_statistik')
	sukses_rebut = fields.Integer(string="Interception",compute='_compute_statistik')
	pelanggaran = fields.Integer(string="Fouls",compute='_compute_statistik')
	kartu_kuning = fields.Integer(string="Yellow Card",compute='_compute_statistik')
	kartu_merah = fields.Integer(string="Red Card",compute='_compute_statistik')
	offsides = fields.Integer(string="Offsides",compute='_compute_statistik')
	sapu_bersih = fields.Integer(string="Clearances",compute='_compute_statistik')
	penghadangan = fields.Integer(string="Block",compute='_compute_statistik')
	penyelamatan = fields.Integer(string="Saves",compute='_compute_statistik')
	gol_kick = fields.Integer(string="Goal Kick",compute='_compute_statistik')
	gol = fields.Integer(string="Goal",compute='_compute_statistik')
	drible_sukses = fields.Integer(string="Dribble",compute='_compute_statistik')
	lepas_control = fields.Integer(string="Possession Loss",compute='_compute_statistik')
	sundulan_kepala = fields.Integer(string="Aerial",compute='_compute_statistik')
	passing_sukses = fields.Integer(string="Passes",compute='_compute_statistik')
	passing_gagal = fields.Integer(string="Key. Passes",compute='_compute_statistik')
	assist = fields.Integer(string="Assist.",compute='_compute_statistik')
	rating_ids = fields.One2many('persebaya.rating','employee_id',string="Rating & Review")
	club_id = fields.Many2one('persebaya.club', string="Club")
	status_pemain = fields.Selection([
		('siap', 'Ready To Play'),
		('belum', 'Not Ready'),
	], string="Status Pemain", default='belum')
	no_punggung = fields.Integer(string="Player Number")
	rating = fields.Selection([
		('0', 'No rating'),
		('1', '1 Star'),
		('2', '2 Star'),
		('3', '3 Star'),
		('4', '4 Star'),
		('5', '5 Star'),
	], string='Rating',readonly=True,compute='_compute_rating')


	def _compute_rating(self):
		for s in self:
			if len(s.rating_ids)>0:
				rating = sum([rat.rating for rat in s.rating_ids]) / len(s.rating_ids)
				s.rating = str(rating)
	
	@api.one
	def _compute_statistik(self):
		self.tekel_sukses = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Tackles')]))
		self.sukses_rebut = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Interception')]))
		self.pelanggaran = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Fouls')]))
		self.kartu_kuning = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Yellow Card')]))
		self.kartu_merah = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Red Card')]))
		self.offsides = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Offsides')]))
		self.sapu_bersih = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Clearances')]))
		self.penghadangan = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Block')]))
		self.penyelamatan = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Saves')]))
		self.gol_kick = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Goal Kick')]))
		self.gol = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Goal')]))
		self.drible_sukses = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Dribble')]))
		self.lepas_control = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Possession Loss')]))
		self.sundulan_kepala = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Aerial')]))
		self.passing_sukses = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Passes')]))
		self.passing_gagal = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Key. Passes')]))
		self.assist = len(self.env['persebaya.moments'].search([('players_moments','=',self.id),('moments','=','Assist')]))