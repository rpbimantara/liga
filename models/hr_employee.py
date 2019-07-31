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


	

