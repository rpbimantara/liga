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
	ob = fields.Integer(string="Open Bid")
	inc = fields.Integer(string="Increment")
	binow = fields.Integer(string="BIN")
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
	product_id = fields.Many2one('product.template',string="Product")
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

	@api.model
	def create(self,vals):
		res = super(BidLelangPersebaya,self).create(vals)
		if res.keterang ==  'BID':
			res.product_id.write({
				'ob'		 : res.product_id.ob + res.product_id.inc,
				'list_price' : res['nilai'],
			})

		if res.keterang ==  'BIN' or res.nilai >= res.product_id.binow:
			res.product_id.write({
				'list_price' : res['nilai'],
				'status_lelang'  : 'selesai',
				'pemenang'		 : res.user_bid.id
			})
			# order_id = res.env['sale.order'].search([('partner_id','=',res.user_bid.partner_id.id),('state','=','draft')])
			# if order_id:
			# 	res.env['sale.order.line'].create({
			# 		'product_id' : res.product_id.product_variant_id.id,
			# 		'order_id'	: order_id.id
			# 	})
			# else:
			sale_id = res.env['sale.order'].create({
				'partner_id' : res.user_bid.partner_id.id,
				'user_id' : res.product_id.create_uid.id,
				'payment_term_id' : 1
			})
			if sale_id:
				res.env['sale.order.line'].create({
					'product_id' : res.product_id.product_variant_id.id,
					'order_id'	: sale_id.id
				})
				sale_id.action_confirm()
				sale_id.action_invoice_create()
		return res