from odoo import api, fields, models
import json
from pyfcm import FCMNotification

class ProductTemplateInherits(models.Model):
	_inherit = "product.template"

	variant_text = fields.Text(String="Variant")
	type = fields.Selection(selection_add=[('lelang', 'Auction'),('donasi', 'Donation')])
	ob = fields.Integer(string="Open Bid")
	inc = fields.Integer(string="Increment")
	binow = fields.Integer(string="BIN")
	due_date = fields.Datetime(string="End Date")
	pemenang = fields.Many2one('res.users',string="Winner",readonly=True)
	bid_ids = fields.One2many('persebaya.lelang.bid','product_id',string="Auction History")
	donasi_ids = fields.One2many('persebaya.donasi','product_id',string="Donation History")
	target_donasi = fields.Integer(string="Target")
	status_lelang = fields.Selection([
		('tolak', 'Refuse'),
		('draft', 'Draft'),
		('jalan', 'On Progress'),
		('selesai', 'End'),
	], string="State", default='draft', readonly=True)
	status_donasi = fields.Selection([
		('tolak', 'Refuse'),
		('draft', 'Draft'),
		('jalan', 'On Progress'),
		('selesai', 'End'),
	], string="State", default='draft', readonly=True)

	# @api.onchange('status_lelang')
	# def _onchange_status_lelang(self):
	# 	if self.status_lelang == 'selesai' and self.pemenang:

	@api.model
	def create_product(self,image_medium,name,list_price,qty,description_sale,create_uid):
		try:
			with self.env.cr.savepoint():
				vals = []
				product_data = {
							'image_medium':image_medium,
							'name':name,
							'list_price':list_price,
							'description_sale':description_sale,
							'purchase_ok':False,
							'type':'product'
						}
				template_id = self.env['product.template'].sudo().create(product_data)
				template_id.write({'create_uid':create_uid})
				product_id = self.env['product.product'].search([('product_tmpl_id','=',template_id.id)])
				stock =self.update_qty(product_id.id,qty)
				
				data = {'name':'create'}
				vals.append(data)
				return vals
		except Exception as e:
			raise e
	
	@api.model
	def update_qty(self,template_id,qty):
		product_id = self.env['product.product'].search([('product_tmpl_id','=',template_id)])
		stock_quant = self.env['stock.quant'].sudo().create({
					'product_id':product_id.id,
					'qty':qty,
					'location_id':15
				})
		return stock_quant.id

	def action_refuse_donasi(self):
		self.write({'status_donasi' : 'tolak'})
		message_title = "Persebaya Fans Donation"
		message_body  = "Your donation (" + self.name + ") has been refused."
		data = {'id': self.id}
		self.push_pyfcm_multi( message_title, message_body, data)
		self.send_mail(message_title,message_body)

	def action_valid_donasi(self):
		self.write({'status_donasi' : 'jalan'})
		message_title = "Persebaya Fans Donation"
		message_body  = "Your donation (" + self.name + ") is on progres."
		data = {'id': self.id}
		self.push_pyfcm_multi( message_title, message_body, data)
		self.send_mail(message_title,message_body)


	def action_end_donasi(self):
		self.write({'status_donasi' : 'selesai'})
		message_title = "Persebaya Fans Donation"
		message_body  = "Your donation (" + self.name + ") has been ended."
		data = {'id': self.id}
		self.push_pyfcm_multi( message_title, message_body, data)
		self.send_mail(message_title,message_body)
			

	def action_refuse_lelang(self):
		self.write({'status_donasi' : 'tolak'})
		message_title = "Persebaya Fans Auction"
		message_body  = "Your auction items (" + self.name + ") has been refused."
		data = {'id': self.id}
		self.push_pyfcm_multi( message_title, message_body, data)
		self.send_mail(message_title,message_body)

	def action_valid_lelang(self):
		self.write({'status_donasi' : 'jalan'})
		message_title = "Persebaya Fans Auction"
		message_body  = "Your auction items (" + self.name + ") is on progres."
		data = {'id': self.id}
		self.push_pyfcm_multi(message_title, message_body, data)
		self.send_mail(message_title,message_body)

	def action_end_lelang(self):
		self.write({'status_donasi' : 'selesai'})
		message_title = "Persebaya Fans Auction"
		message_body  = "Your auction items (" + self.name + ") finished. Send it to the winner :" + self.pemenang.name
		data = {'id': self.id}
		self.push_pyfcm_multi(message_title, message_body, data)
		self.send_mail(message_title,message_body)
			
	def push_pyfcm_multi(self, message_title, message_body, data=False):
		users = self.env['res.users'].search([('id','=',self.create_uid.id),('fcm_reg_ids','!=',False)])
		fcm_regids = [i.fcm_reg_ids.encode('ascii','ignore') for i in users]
		push_service = FCMNotification(api_key=self.env.user.company_id.api_key)
		result = push_service.notify_multiple_devices(registration_ids=fcm_regids, 
		message_title=message_title,
		message_body=message_body)
		print(result)

	def send_mail(self,message_title,message_body):
		# user = self.env['res.users'].browse(current_uid)
		self.env['mail.message'].create({'message_type':"notification",
					"subtype": self.env.ref("mail.mt_comment").id, # subject type
					'body': message_body,
					'subject': message_title,
					'partner_ids' : [(4, self.create_uid.partner_id.id)],
					'needaction_partner_ids': [(4, self.create_uid.partner_id.id)],   # partner to whom you send notification
					'model': self._name,
					'res_id': self.id,
					})

class ProductProductInherits(models.Model):
	_inherit = "product.product"

	variant_text = fields.Text(String="Variant", compute='_compute_variant_text')


	@api.depends('attribute_line_ids')
	def _compute_variant_text(self):
		for s in self:
			text_string = ""
			# if len(s.attribute_value_ids) > 0 :
			for a in s.attribute_value_ids:
				text_string += a.name +"\n "
			# text_string = text_string.rstrip(', ')
			s.variant_text = text_string
		
	@api.model
	def get_detail_store(self,template_id):
		product_ids = self.env['product.product'].search([('product_tmpl_id','=',template_id)])
		vals = []
		for product in product_ids:
			variant_text = ""
			for variant in product.attribute_value_ids:
				variant_text +=  variant.attribute_id.name + " : " + variant.name +", "
			variant_text = variant_text.rstrip(', ')
			data = {
				'id' : product.id,
				'name': product.name,
				'image' : product.image_medium,
				'variant' : variant_text,
				'qty_available' : product.qty_available,
				'desc' : product.description_sale,
				'owner' : product.create_uid.id,
				'ownername' : product.create_uid.name,
				'date' : product.create_date
			}
			vals.append(data)
		return vals

class SaleOrderInherits(models.Model):
	_inherit = "sale.order"

	# @api.model
	# def search_so(self,value,lines):
	# 	so = self.env['sale.order'].sudo().search([('partner_id','=',value),('state','=','draft')])
	# 	return so

	@api.model
	def create_so(self,value,lines):
		try:
			with self.env.cr.savepoint():
				vals = []
				sale_id = self.env['sale.order'].sudo().create({
						'partner_id':value,
						'payment_term_id':1,
						'user_id':1
					})
				if  len(lines)> 0:
					for l in lines:
						self.env['sale.order.line'].create({
							'order_id':sale_id.id,
							'product_id':l.get('product_id'),
							'event_id':l.get('event_id'),
							'event_ticket_id':l.get('event_ticket_id'),
							'product_uom_qty':l.get('product_uom_qty')
						})
					
				data = {'id':sale_id.id}
				vals.append(data)
				return vals
		except Exception as e:
			raise e

	@api.model
	def create_so_checkout(self,value,lines):
		try:
			with self.env.cr.savepoint():
				vals = []
				sale_id = self.env['sale.order'].sudo().create({
						'partner_id':value,
						'payment_term_id':1,
						'user_id':1
					})
				for l in lines:
					self.env['sale.order.line'].create({
						'order_id':sale_id.id,
						'product_id':l.get('product_id'),
						'event_id':l.get('event_id'),
						'event_ticket_id':l.get('event_ticket_id'),
						'product_uom_qty':l.get('product_uom_qty')
					})
					
				data = {'id':sale_id.id}
				vals.append(data)
				return vals
		except Exception as e:
			raise e

	@api.model
	def confirm_so(self,value):
		confirm = self.sudo()._confirm_so(value)
		return [{'id':confirm}]

	@api.multi
	def _confirm_so(self,value):
		sale_id = self.env['sale.order'].browse(value)
		# sale_id._action_procurement_create()
		sale_id.action_confirm()
		# sale_id.order_line._update_registrations(confirm=sale_id.amount_total == 0, cancel_to_draft=False)
		invoice = sale_id.sudo().action_invoice_create()
		invoice_id = self.env['account.invoice'].browse(invoice[0])
		invoice_id.sudo().action_invoice_open()
		invoice_id.sudo().pay_and_reconcile(self.env['account.journal'].search([('type', '=', 'cash')], limit=1), invoice_id.amount_total)
		invoice_id.mapped('invoice_line_ids.sale_line_ids')._update_registrations(confirm=True)
		# sale_id.picking_ids.action_done()
		self.notify_customer(sale_id.partner_id.id)
		picking = self.env['stock.picking'].search([('id','in',[sale_id.picking_ids.id]),('state','!=','done')])
		for pick in picking:
			for product in pick.move_lines:
				self.notify_seller(
					pick.partner_id.name,
					pick.partner_id.street,
					product.product_id.create_uid.partner_id.id,
					product.product_id.name,
					str(product.ordered_qty))
				# ctx = { 'active_model': 'account.invoice', 'active_ids': [invoice_id.id] }
				# register_payments = self.env['account.register.payments'].with_context(ctx).sudo().create()
				# print(register_payments)
				# payment_id = register_payments.sudo().create_payment()
				# print(payment_id)
				# invoice_id.sudo().action_invoice_paid()
		return invoice_id.id
	
	def notify_customer(self,partner_id):
		users = self.env['res.users'].search([('partner_id','=',partner_id)])
		fcm_regids = [i.fcm_reg_ids.encode('ascii','ignore') for i in users]
		message_title = "Persebaya Fans Store"
		message_body  = "Your order is on progress"
		data = {'id': self.id}
		self.push_pyfcm_multi(fcm_regids, message_title, message_body, data)
		self.send_mail(message_title,message_body,partner_id)
	
	def notify_seller(self,partner_name,partner_street,seller_id,product_name,product_qty):
		users = self.env['res.users'].search([('partner_id','=',seller_id)])
		fcm_regids = [i.fcm_reg_ids.encode('ascii','ignore') for i in users]
		message_title = "Persebaya Fans Store"
		message_body  = partner_name + " buy your items "+ product_name +" ("+product_qty+") send it to : " +partner_street+"."
		data = {'id': self.id}
		self.send_mail(message_title,message_body,seller_id)
		self.push_pyfcm_multi(fcm_regids, message_title, message_body, data)

	def push_pyfcm_multi(self, to_regids, message_title, message_body, data=False):
		push_service = FCMNotification(api_key=self.env.user.company_id.api_key)
		result = push_service.notify_multiple_devices(registration_ids=to_regids, 
		message_title=message_title,
		message_body=message_body)
		print(result)

	def send_mail(self,message_title,message_body,partner_id):
		# user = self.env['res.users'].browse(current_uid)
		self.env['mail.message'].create({'message_type':"notification",
					"subtype": self.env.ref("mail.mt_comment").id, # subject type
					'body': message_body,
					'subject': message_title,
					'partner_ids' : [(4, partner_id)],
					'needaction_partner_ids': [(4, partner_id)],   # partner to whom you send notification
					'model': self._name,
					'res_id': self.id,
					})

class SaleOrderLineInherits(models.Model):
	_inherit = "sale.order.line"

	@api.model
	def get_checkout_list(self,partner_id):
		vals = []
		order_id = self.env['sale.order'].search([('partner_id','=',partner_id),('state','=','draft')]).id
		order_ids = self.env['sale.order.line'].search([('order_id','=',order_id)])
		for order in order_ids:
			data = {
					'id'	: order.id,
					'nama'	: order.product_id.name,
					'type'	: order.product_id.type,
					'harga'	: order.price_unit,
					'qty'	: order.product_uom_qty,
					'image'	: order.product_id.image_medium,
					'stock' : order.product_id.qty_available
				}
			vals.append(data)
		return vals


class DonasiPersebaya(models.Model):
	_name = 'persebaya.donasi'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	product_id = fields.Many2one('product.template',string="Product")
	user_bid = fields.Many2one('res.users',string="Participant")
	nilai = fields.Integer(string="Nominal",required=True)
	keterang = fields.Char(string="Note")

	@api.model
	def create(self,vals):
		res = super(DonasiPersebaya,self).create(vals)
		res.product_id.write({
				'list_price' : res.product_id.list_price + res['nilai'],
			})
		sale_id = res.env['sale.order'].create({
				'partner_id' : res.user_bid.partner_id.id,
				'user_id' : res.product_id.create_uid.id,
				'payment_term_id' : 1
			})
		if sale_id:
			res.env['sale.order.line'].create({
					'product_id' : res.product_id.product_variant_id.id,
					'order_id'	: sale_id.id,
					'price_unit':res['nilai']
				})
			sale_id.action_confirm()
			invoice = sale_id.action_invoice_create()
			invoice_id = self.env['account.invoice'].browse(invoice[0])
			invoice_id.sudo().action_invoice_open()
			invoice_id.sudo().pay_and_reconcile(self.env['account.journal'].search([('type', '=', 'cash')], limit=1), invoice_id.amount_total)
		return res