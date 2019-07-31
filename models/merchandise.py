# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MerchandisePersebaya(models.Model):
	_name = 'persebaya.merchandise'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	active = fields.Boolean(default=True, help="The active field allows you to hide the merchandise without removing it.",track_visibility='onchange')
	code_barang = fields.Char(string="Kode Barang",required=True,track_visibility='onchange')
	nama_barang = fields.Char(string="Nama Barang",required=True,track_visibility='onchange')
	harga_barang = fields.Integer(string="Harga Barang",required=True,track_visibility='onchange')
	status_stock = fields.Selection([
		('in', 'In Stock'),
		('out', 'Out of Stock'),
	], string="Status Stock", default='out',compute='_compute_stock_total_barang',track_visibility='onchange')
	stock_total_barang = fields.Integer(string="Jumlah Stock",readonly=True,compute='_compute_ukuran_lines',track_visibility='onchange')
	deskripsi_barang = fields.Text(string="Deskripsi",track_visibility='onchange')
	image = fields.Binary(string="Foto Barang",track_visibility='onchange')
	status_merch = fields.Selection([
		('ofc', 'Official Merchandise'),
		('non', 'Non-Official'),
	], string="Status Merchandise", default='ofc', readonly=True,track_visibility='onchange')
	ukuran_lines = fields.One2many('persebaya.merchandise.line','merchandise_id',string="Stock Ukuran",track_visibility='onchange')
	kategori_ukuran = fields.Many2one('persebaya.ukuran',string="Kategori Ukuran",track_visibility='onchange')

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			code = s.code_barang or ''
			nama = s.nama_barang or ''
			res.append((s.id,code + ' - ' + nama))

		return res

	@api.depends('ukuran_lines')
	def _compute_ukuran_lines(self):
		for s in self:
			total = 0
			for l in s.ukuran_lines:
				total += l.stock_ukuran

			s.stock_total_barang = total

	@api.depends('stock_total_barang')
	def _compute_stock_total_barang(self):
		for s in self:
			if s.stock_total_barang > 0:
				s.status_stock = 'in'
			else:
				s.status_stock = 'out'

	def create_merchandise_line(self,ukuran_id,merchandise_id):
		line = self.env['persebaya.ukuran.lines'].search([('ukuran_id','=',ukuran_id)])
		if len(line) < 1:
			raise ValidationError('Ukuran tidak ditemukan silahkan buat ukuran atau pilih kategori lain!')
		else:
			for l in line:
				data = {
					'merchandise_id':merchandise_id,
					'ukuran_barang':l.name,
					'detail_ukuran':l.detail_ukuran
				}
				self.env['persebaya.merchandise.line'].create(data)

	@api.multi
	@api.onchange('kategori_ukuran')
	def _onchange_stock_tota_barang(self):
		self_id = self._origin.id
		for s in self:
			if s.kategori_ukuran:
				if len(s.ukuran_lines) > 0:
					sql = """DELETE FROM persebaya_merchandise_line WHERE merchandise_id = %s;"""%(str(self_id),)
					s._cr.execute(sql)
					s.create_merchandise_line(s.kategori_ukuran.id,self_id)
				else:
					s.create_merchandise_line(s.kategori_ukuran.id,self_id)

	# @api.multi
	# def open_list_update_stock(self):
	# 	action = self.env.ref('persebaya.action_show_history_stock')
	# 	result = action.read()[0]
	# 	temp_ids = [stock.id for stock in self.env['persebaya.update.stock'].search([('merchandise_id','=',self.id)])]
	# 	print temp_ids
	# 	result['domain'] = [('id', 'in', temp_ids)]
	# 	return result

	# @api.multi
	# def open_list_update_harga(self):
	# 	action = self.env.ref('persebaya.action_show_history_harga')
	# 	result = action.read()[0]
	# 	temp_ids = [stock.id for stock in self.env['persebaya.update.harga'].search([('merchandise_id','=',self.id)])]
	# 	print temp_ids
	# 	result['domain'] = [('id', 'in', temp_ids)]
	# 	return result

class LineMerchandisePersebaya(models.Model):
	_name = 'persebaya.merchandise.line'

	merchandise_id = fields.Many2one('persebaya.merchandise',string="Barang",readonly=True)
	ukuran_barang = fields.Char(string="Ukuran",readonly=True)
	detail_ukuran = fields.Text(string="Detail ukuran",readonly=True)
	stock_ukuran = fields.Integer(string="Stock")
	
	@api.multi
	def name_get(self):
		res = []
		for s in self:
			ukuran = s.ukuran_barang or ''
			res.append((s.id, ukuran))

		return res