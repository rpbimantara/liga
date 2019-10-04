from odoo import fields, models,api

class HrEmployeeInherit(models.Model):
	_inherit = 'hr.employee'

	tekel_sukses = fields.Integer(string="Tackles")
	sukses_rebut = fields.Integer(string="Interception")
	pelanggaran = fields.Integer(string="Fouls")
	kartu_kuning = fields.Integer(string="Yellow Card")
	kartu_merah = fields.Integer(string="Red Card")
	offsides = fields.Integer(string="Offsides")
	sapu_bersih = fields.Integer(string="Clearances")
	penghadangan = fields.Integer(string="Block")
	penyelamatan = fields.Integer(string="Saves")
	gol_kick = fields.Integer(string="Goal Kick")
	gol = fields.Integer(string="Goal")
	drible_sukses = fields.Integer(string="Dribble")
	lepas_control = fields.Integer(string="Possession Loss")
	sundulan_kepala = fields.Integer(string="Aerial")
	passing_sukses = fields.Integer(string="Passes")
	passing_gagal = fields.Integer(string="Key. Passes")
	assist = fields.Integer(string="Assist.")
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
		('Key. Passes', ''),
		('.', 'Assist.'),