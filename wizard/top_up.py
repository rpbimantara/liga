from odoo import models, fields, api
from odoo.exceptions import UserError

class PersebayaTopup(models.Model):
	_name = 'persebaya.topup'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	nik = fields.Char(string="NIK",size=16)
	nama = fields.Many2one('res.partner',string="Name",readonly=True)
	saldo_terkini = fields.Integer(related='nama.saldo',string="Coin",readonly=True)
	topup = fields.Integer(string="Top Up Value")

	@api.onchange('nik')
	def _get_partner(self):
		if self.nik:
			partner_id = self.env['res.partner'].search([('nik','=',self.nik)])
			self.nama = partner_id.id

	def proses_top_up(self):
		if self.nama:
			# if self.topup
			# raise UserError('Jumlah amount harus sama dengan jumlah amount di pengajuan bank!')
			saldo = self.saldo_terkini + self.topup
			self.nama.saldo = saldo