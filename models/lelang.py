# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class LelangPersebaya(models.Model):
	_name = 'persebaya.lelang'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	nama_barang = fields.Char(string="Name",required=True)
	active = fields.Boolean(default=True, help="Uncheck if your item is second item.")
	foto_lelang = fields.Binary(string="Picture",required=True)
	deskripsi_barang = fields.Text(string="Description")
	ob = fields.Integer(string="Open Bid",required=True)
	inc = fields.Integer(string="Increment",required=True,readonly=False)
	binow = fields.Integer(string="BIN",required=True)
	due_date = fields.Datetime(string="End Date")
	pemenang = fields.Many2one('res.users',string="Winner",readonly=True)
	bid_ids = fields.One2many('persebaya.lelang.bid','lelang_id',string="Lelang History")
	status_lelang = fields.Selection([
		('jalan', 'Berjalan'),
		('selesai', 'Selesai'),
	], string="State", default='jalan', readonly=True)
	create_uid = fields.Many2one('res.users',default=lambda self: self.env.user.id)

	@api.multi
	def name_get(self):
		res = []
		for s in self:
			nama = s.nama_barang or ''
			res.append((s.id,nama))
		return res


	def selisih_waktu(self):
		datalelang = self.env['persebaya.lelang'].search([('status_lelang','=','jalan')])
		for s in datalelang:
			if datetime.strptime(s.due_date, '%Y-%m-%d %H:%M:%S') <= datetime.now():
				s.status_lelang = "selesai"

	def lelang_notification(self):
		for s in self:
			bid_ids = s.env['persebaya.lelang.bid'].search([('lelang_id','=',s.id)])
			if bid_ids:
				s.write({'inc':bid_ids[0].nilai + bid_ids[-1].nilai})

	def list_lelang(self):
		vals = []
		lelang_ids = self.env['persebaya.lelang'].search([('status_lelang','=','jalan')])
		bider = 0
		for lelang in lelang_ids:
			if len(lelang.bid_ids) < 1:
				bider = lelang.ob
			else:
				bider = lelang.bid_ids[-1].nilai + lelang.inc
			data = {
			'idlelang' : lelang.id,
			'namalelang' : lelang.nama_barang,
			'lelangimage' : lelang.foto_lelang,
			'waktulelang' : lelang.due_date,
			'bidlelang' : bider,
			'binlelang' : lelang.binow,
			'inclelang' : lelang.inc,
			'pemiliklelang' : lelang.create_uid.id
			}
			vals.append(data)
		return vals

class BidLelangPersebaya(models.Model):
	_name = 'persebaya.lelang.bid'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	lelang_id = fields.Many2one('persebaya.lelang',string="Lelang")
	user_bid = fields.Many2one('res.users',string="Participant")
	nilai = fields.Integer(string="Nominal",required=True)
	keterang = fields.Char(string="Note")

	# @api.multi
	# def name_get(self):
	# 	res = []
	# 	for s in self:
	# 		user = s.user_bid.name or ''
	# 		nilai = s.nilai or ''
	# 		ket = s.keterang or ''
	# 		res.append((s.id,user + ' - ' + ket + ' - ' + nilai))

	# 	return res