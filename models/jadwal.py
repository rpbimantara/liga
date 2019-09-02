# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from pyfcm import FCMNotification
import json

class PersebayaJadwal(models.Model):
	_name = 'persebaya.jadwal'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	liga_id = fields.Many2one('persebaya.liga',string="League",readonly=False)
	tgl_main = fields.Datetime(string="Date")
	durasi = fields.Integer(string="Durasi Main")
	stadion_id = fields.Many2one(related='home.stadion',string="Venue")
	home = fields.Many2one('persebaya.club', string="Team Home")
	away = fields.Many2one('persebaya.club', string="Team Away")
	wasit = fields.Char(string="Referee")
	hakim1 = fields.Char(string="Judge 1")
	hakim2 = fields.Char(string="Judge 2")
	wasit_cadangan = fields.Char(string="Reserve Referee")
	inspektur = fields.Char(string="Inspector Referee")
	match_comm = fields.Char(string="Match Commisioner")
	general_coor = fields.Char(string="General Coordinator")
	media_ofc = fields.Char(string="Media Officer")
	hasil = fields.Selection([
		('home', 'Home Win'),
		('draw', 'Draw'),
		('away', 'Away Win')
	], string="Result")
	status_jadwal = fields.Selection([
		('valid', 'Valid'),
		('akan', 'Incoming'),
		('tunda', 'Postponed'),
		('main', 'Play'),
		('selesai', 'Done'),
	], string="Status Jadwal", default='akan')
	pelatih_home = fields.Many2one(related='home.pelatih',string="Coach Home",readonly=True)
	formasi_home = fields.Char(string="Formation Team")
	ht_home = fields.Char(string="Half Time",readonly=True,compute='_compute_match_detail')
	ft_home = fields.Char(string="Full Time",readonly=True,compute='_compute_match_detail')
	xt_home = fields.Char(string="Extra Time",readonly=True,compute='_compute_match_detail')
	pinalty_home = fields.Char(string="Penalty",readonly=True,compute='_compute_match_detail')
	pelatih_away = fields.Many2one(related='away.pelatih',string="Coach Away",readonly=True)
	formasi_away = fields.Char(string="Formation Team")
	ht_away = fields.Char(string="Half Time",readonly=True,compute='_compute_match_detail')
	ft_away = fields.Char(string="Full Time",readonly=True,compute='_compute_match_detail')
	xt_away = fields.Char(string="Extra Time",readonly=True,compute='_compute_match_detail')
	pinalty_away = fields.Char(string="Penalty",readonly=True,compute='_compute_match_detail')
	kuning_home = fields.Char(string="Yellow Card",readonly=True,compute='_compute_match_detail')
	kuning_away = fields.Char(string="Yellow Card",readonly=True,compute='_compute_match_detail')
	merah_home = fields.Char(string="Red Card",readonly=True,compute='_compute_match_detail')
	merah_away = fields.Char(string="Red Card",readonly=True,compute='_compute_match_detail')
	penguasaan_home = fields.Integer(string="Ball Possession (%)")
	penguasaan_away = fields.Integer(string="Ball Possession (%)")
	tembakan_home = fields.Char(string="Shots",readonly=True,compute='_compute_match_detail')
	tembakan_away = fields.Char(string="Shots",readonly=True,compute='_compute_match_detail')
	pelanggaran_home = fields.Char(string="Fouls",readonly=True,compute='_compute_match_detail')
	pelanggaran_away = fields.Char(string="Fouls",readonly=True,compute='_compute_match_detail')
	sudut_home = fields.Char(string="Corners",readonly=True,compute='_compute_match_detail')
	sudut_away = fields.Char(string="Corners",readonly=True,compute='_compute_match_detail')
	offside_home = fields.Char(string="Offsides",readonly=True,compute='_compute_match_detail')
	offside_away = fields.Char(string="Offsides",readonly=True,compute='_compute_match_detail')
	penyelamatan_home = fields.Char(string="Saves",readonly=True,compute='_compute_match_detail')
	penyelamatan_away = fields.Char(string="Saves",readonly=True,compute='_compute_match_detail')
	home_ids = fields.One2many('persebaya.line.up.home','jadwal_id',string="DSP")
	away_ids = fields.One2many('persebaya.line.up.away','jadwal_id',string="DSP")
	moments_ids = fields.One2many('persebaya.moments','jadwal_id')

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			if s.tgl_main:
				tgl = datetime.strptime(s.tgl_main, '%Y-%m-%d %H:%M:%S') +  timedelta(hours=7) or ''
			else:
				tgl = ''
			home = s.home.nama or ''
			away = s.away.nama or ''
			res.append((s.id, str(tgl) + ' - ' + home + ' vs ' + away))

		return res

	@api.multi
	def action_tunda(self):
		self.write({'status_jadwal': 'tunda'})

	@api.multi
	def action_match(self):
		self.write({'status_jadwal': 'main'})
		self.detail()

	@api.multi
	def action_valid(self):
		self.write({'status_jadwal': 'valid'})

	@api.multi
	def action_done(self):
		if self.ht_home > self.ht_away:
			self.write({'hasil': 'home'})
		elif self.ht_home < self.ht_away:
			self.write({'hasil': 'away'})
		else:
			self.write({'hasil': 'draw'})
		self.write({'status_jadwal': 'selesai'})
		
	def open_list_moment(self):
		action = self.env.ref('persebaya.action_show_list_moment')
		result = action.read()[0]
		# temp_ids = [id_petak.area_id.id for id_petak in self.register_id.register_line_ids]
		# print temp_ids
		result['domain'] = [('jadwal_id', '=', self.id)]
		return result

	@api.model
	def jadwal_terkini(self,club_id,liga_id):
		vals = []
		data = {}
		date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		jadwal_ids = self.env['persebaya.jadwal'].search(['|',('away','=',club_id),('home','=',club_id),('tgl_main','<',date),('liga_id','=',liga_id)],limit=1,order="id desc")
		nexts = self.env['persebaya.jadwal'].search(['|',('away','=',club_id),('home','=',club_id),('tgl_main','>',date),('liga_id','=',liga_id)],limit=2)
		skornow = ''
		if nexts[0].status_jadwal  == 'main' or nexts[0].status_jadwal == 'selesai':
			skornow = nexts[0].ft_home + ' - ' + nexts[0].ft_away
		else:
			skornow = ' VS '

		data = {
				'id_last' : jadwal_ids[0].id,
				'image_home_last' :jadwal_ids[0].home.foto_club,
				'image_away_last' : jadwal_ids[0].away.foto_club,
				'home_last' : jadwal_ids[0].home.nama,
				'away_last' : jadwal_ids[0].away.nama,
				'ft_home_last' : jadwal_ids[0].ft_home,
				'ft_away_last' : jadwal_ids[0].ft_away,
				'stadion_last' : jadwal_ids[0].stadion_id.nama,
				'date_last' : str(datetime.strptime(jadwal_ids[0].tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)),
				'liga_last' : jadwal_ids[0].liga_id.nama,
				'id' : nexts[0].id,
				'image_home' :nexts[0].home.foto_club,
				'image_away' : nexts[0].away.foto_club,
				'home' : nexts[0].home.nama,
				'away' : nexts[0].away.nama,
				'ft_home' : nexts[0].ft_home,
				'ft_away' : nexts[0].ft_away,
				'skornow' : skornow,
				'stadion' : nexts[0].stadion_id.nama,
				'date' : str(datetime.strptime(nexts[0].tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)),
				'liga' : nexts[0].liga_id.nama,
				'id_next' : nexts[1].id,
				'image_home_next' :nexts[1].home.foto_club,
				'image_away_next' : nexts[1].away.foto_club,
				'home_next' : nexts[1].home.nama,
				'away_next' : nexts[1].away.nama,
				'ft_home_next' : nexts[1].ft_home,
				'ft_away_next' : nexts[1].ft_away,
				'stadion_next' : nexts[1].stadion_id.nama,
				'date_next' : str(datetime.strptime(nexts[1].tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)),
				'liga_next' : nexts[1].liga_id.nama
			}
		vals.append(data)
		return vals

	@api.model
	def list_jadwal(self,club_id,liga_id):
		vals = []
		jadwal_ids = self.env['persebaya.jadwal'].search(['|',('away','=',club_id),('home','=',club_id),('liga_id','=',liga_id)])
		for jadwal in jadwal_ids:
			date = datetime.strptime(jadwal.tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
			foto_club = ''
			nama_club = ''
			is_home = False
			if jadwal.away.id == club_id:
				foto_club = jadwal.home.foto_club
				nama_club = jadwal.home.nama
				is_home = False
			else:
				foto_club = jadwal.away.foto_club
				nama_club = jadwal.away.nama
				is_home = True
			data = {
			'id' : jadwal.id,
			'nama_club' : nama_club,
			'foto_club' : foto_club,
			'liga_id' : jadwal.liga_id.nama,
			'date' : str(date),
			'stadion' : jadwal.stadion_id.nama,
			'status_jadwal' : jadwal.status_jadwal,
			'is_home' : is_home
			}
			vals.append(data)
		return vals

	@api.model
	def list_jadwal_club(self,club_id,liga_id,status):
		club_id = 42
		liga_id = 11
		status = ['selesai']
		vals = []
		jadwal_ids = self.env['persebaya.jadwal'].search(['|',('away','=',club_id),('home','=',club_id),('status_jadwal','in',[str(item) for item in status]),('liga_id','=',liga_id)])
		for jadwal in jadwal_ids:
			date = datetime.strptime(jadwal.tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
			foto_club = ''
			nama_club = ''
			is_home = False
			if jadwal.away.id == club_id:
				foto_club = jadwal.home.foto_club
				nama_club = jadwal.home.nama
				is_home = False
			else:
				foto_club = jadwal.away.foto_club
				nama_club = jadwal.away.nama
				is_home = True
			data = {
			'id' : jadwal.id,
			'nama_club' : nama_club,
			'foto_club' : foto_club,
			'liga_id' : jadwal.liga_id.nama,
			'date' : str(date),
			'stadion' : jadwal.stadion_id.nama,
			'status_jadwal' : jadwal.status_jadwal,
			'is_home' : is_home
			}
			vals.append(data)
		return vals

	@api.model
	def match_detail(self,id_jadwal):
		vals = []
		jadwal_ids = self.env['persebaya.jadwal'].search([('id','=',id_jadwal)])
		skornow = ''
		if jadwal_ids.status_jadwal  == 'main' or jadwal_ids.status_jadwal == 'selesai':
			skornow = jadwal_ids.ft_home + ' - ' + jadwal_ids.ft_away
		else:
			skornow = ' VS '
		for jadwal in jadwal_ids:
			date = datetime.strptime(jadwal.tgl_main, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
			data = {
				'id' : jadwal.id,
				'liga' : jadwal.liga_id.nama,
				'stadion' : jadwal.stadion_id.nama,
				'date' : date.strftime('%Y-%m-%d %H:%M') + ' WIB',
				'id_home' : jadwal.home.id,
				'home' : jadwal.home.nama,
				'imageHome' : jadwal.home.foto_club,
				'id_away' : jadwal.away.id,
				'away' : jadwal.away.nama,
				'imageAway' : jadwal.away.foto_club,
				'score' : skornow
			}
			vals.append(data)
		return vals

	def detail(self):
		users = self.env['res.users'].search([('active','=',True),('fcm_reg_ids','!=',False)])
		fcm_regids = [i.fcm_reg_ids.encode('ascii','ignore') for i in users]
		message_title = "Persebaya Fans"
		message_body  = "Today is Persebaya Day : " + self.home.nama + " VS " + self.away.nama
		data = {'model':'persebaya.jadwal', 'id': self.id}
		self.push_pyfcm_multi(fcm_regids, message_title, message_body, data)


	def push_pyfcm_multi(self, to_regids, message_title, message_body, data=False):
		push_service = FCMNotification(api_key=self.env.user.company_id.api_key)
		result = push_service.notify_multiple_devices(registration_ids=to_regids, 
		message_title=message_title,
		message_body=message_body)

	@api.one
	@api.depends('moments_ids')
	def _compute_match_detail(self):
		self.ht_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Goal'),('time_moments','<=',45)]))
		self.ft_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Goal')]))
		self.pinalty_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Penalti')]))
		self.kuning_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Yellow Card')]))
		self.merah_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Red Card')]))
		self.tembakan_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Shots')]))
		self.pelanggaran_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Fouls')]))
		self.sudut_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Corner')]))
		self.offside_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Offsides')]))
		self.penyelamatan_home = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.home.id),('moments','=','Saves')]))

		self.ht_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Goal'),('time_moments','<=',45)]))
		self.ft_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Goal')]))
		self.pinalty_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Penalti')]))
		self.kuning_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Yellow Card')]))
		self.merah_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Red Card')]))
		self.tembakan_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Shots')]))
		self.pelanggaran_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Fouls')]))
		self.sudut_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Corner')]))
		self.offside_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Offsides')]))
		self.penyelamatan_away = len(self.env['persebaya.moments'].search([('jadwal_id','=',self.id),('club_id','=',self.away.id),('moments','=','Saves')]))

class PersebayaMoments(models.Model):
	_name = 'persebaya.moments'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	jadwal_id = fields.Many2one('persebaya.jadwal',string="Jadwal",readonly=True)
	time_moments = fields.Char(string="Time")
	moments = fields.Selection([
		('Subtitution', 'Subtitution'),
		('Tackles', 'Tackles'),
		('Interception', 'Interception'),
		('Fouls', 'Fouls'),
		('Yellow Card', 'Yellow Card'),
		('Red Card', 'Red Card'),
		('Offsides', 'Offsides'),
		('Clearances', 'Clearances'),
		('Corners', 'Corners'),
		('Goal Kick', 'Goal Kick'),
		('Goal', 'Goal'),
		('Goal Penalty', 'Goal Penalty'),
		('Dribble', 'Dribble'),
		('Possession Loss', 'Possession Loss'),
		('Aerial', 'Aerial'),
		('Passes', 'Passes'),
		('Key. Passes', 'Key. Passes'),
		('Assist.', 'Assist.'),
	], string="Event",default='Subtitution',required=True)
	home  = fields.Many2one(related='jadwal_id.home',string="Club Home")
	away  = fields.Many2one(related='jadwal_id.away',string="Club Home")
	club_id = fields.Many2one('persebaya.club',string="Club",domain="[('id','in',[home,away])]",required=True)
	players_moments = fields.Many2one('hr.employee',string="Players",domain="[('club_id','=',club_id)]",required=True)
	supp_players_moments = fields.Many2one('hr.employee',string="Support Players",domain="[('club_id','=',club_id)]")

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			club = s.club_id.nama or ''
			moments = s.moments or ''
			res.append((s.id, moments + ' ' + club))

		return res

	# @api.model
	# def create(self,vals):
	# 	res = super(PersebayaMoments,self).create(vals)
	# 	print vals.get('res_id')
	# 	self.push_notify(vals)
	# 	return res

	# def push_notify(self,vals):
	# 	users = self.env['res.users'].search([('active','=',True),('fcm_reg_ids','!=',False)])
	# 	fcm_regids = [i.fcm_reg_ids.encode('ascii','ignore') for i in users]
	# 	moments_ids = self.env['persebaya.moments'].search([('id','=',vals.get('res_id'))])
	# 	home = ''
	# 	away = self.away.nama or ''
	# 	moments = self.moments or ''
	# 	player = self.players_moments.name or ''
	# 	club_id = self.club_id.nama or ''
	# 	message_title = home + " VS " + away
	# 	message_body  = moments + "  " + player + " from " + club_id
	# 	data = {'model':'persebaya.moments', 'id': ''}
	# 	self.push_pyfcm_multi(fcm_regids, message_title, message_body, data)


	# def push_pyfcm_multi(self, to_regids, message_title, message_body, data=False):
	# 	push_service = FCMNotification(api_key=self.env.user.company_id.api_key)
	# 	result = push_service.notify_multiple_devices(registration_ids=to_regids, 
	# 	message_title=message_title,
	# 	message_body=message_body)

class PersebayaLineUpHome(models.Model):
	_name = 'persebaya.line.up.home'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	jadwal_id = fields.Many2one('persebaya.jadwal',string="Jadwal",readonly=True)
	home = fields.Many2one(related='jadwal_id.home',string="Club Home")
	player_id = fields.Many2one('hr.employee',string="Players",domain="[('club_id','=',home)]")
	department_id = fields.Many2one(related='player_id.department_id',string="Department",readonly=True)
	job_id = fields.Many2one(related='player_id.job_id',string="Position",readonly=True)
	no_punggung = fields.Integer(related='player_id.no_punggung',string="Players No.",readonly=True)
	status_pemain = fields.Selection([
		('core', 'Core'),
		('subtitute', 'Subtitute')
	], string='Status Pemain',default='core')

class PersebayaLineUpAway(models.Model):
	_name = 'persebaya.line.up.away'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	jadwal_id = fields.Many2one('persebaya.jadwal',string="Jadwal",readonly=True)
	away = fields.Many2one(related='jadwal_id.away',string="Club Away")
	player_id = fields.Many2one('hr.employee',string="Players",domain="[('club_id','=',away)]")
	department_id = fields.Many2one(related='player_id.department_id',string="Department",readonly=True)
	job_id = fields.Many2one(related='player_id.job_id',string="Position",readonly=True)
	no_punggung = fields.Integer(related='player_id.no_punggung',string="Players No.",readonly=True)
	status_pemain = fields.Selection([
			('core', 'Core'),
			('subtitute', 'Subtitute')
		], string='Status Pemain',default='core')