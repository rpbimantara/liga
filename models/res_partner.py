from odoo import fields, models, api

class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	nik = fields.Char(string="NIK",required=True)
	tgl_lahir = fields.Date(string="Birthday")
	jeniskelamin = fields.Selection([
		('Man', 'Man'),
		('Woman', 'Woman'),
	], string="Gender", default='Man')
	saldo = fields.Integer(string="Coin",compute='_compute_saldo')
	komunitas = fields.Char(string="Community")
	invoice_ids = fields.One2many('account.invoice', 'partner_id', string='History Coin',domain=[('type','=','in_invoice'),('state','=','paid')])
	state = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Valid')
	], string='State',default='draft')
	property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
		string="Account Receivable", oldname="property_account_receivable",
		domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
		help="This account will be used instead of the default one as the receivable account for the current partner",
		required=False)

	property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
		string="Account Payable", oldname="property_account_payable",
		domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
		help="This account will be used instead of the default one as the payable account for the current partner",
		required=False)

	@api.model
	def create(self,vals):
		res = super(ResPartnerInherit,self).create(vals)
		res['supplier'] = True
		return res

	@api.multi
	def action_validate(self):
		self.write({'state': 'validate'})

	@api.one
	def _compute_saldo(self):
		if self.user_ids.id:
			sql = """SELECT l.id,l.name,l.create_date,i.amount_total,i.amount_tax from account_invoice i, account_invoice_line l, product_product p
					WHERE i.id = l.invoice_id AND p.id = l.product_id
					AND i.state = 'paid' AND i.type = 'out_invoice'
					AND p.create_uid = %s"""
			self._cr.execute(sql, (self.user_ids.id,))
			sales_ids = self._cr.dictfetchall()
			customer_ids = self.env['account.invoice'].search([('partner_id','=',self.id),('type','=','out_invoice'),('state','=','paid')])
			# salesperson_ids = self.env['account.invoice'].search([('user_id','=',self.user_ids.id),('type','=','out_invoice'),('state','=','paid')])
			purchase_ids = self.env['account.invoice'].search([('partner_id','=',self.id),('type','in',['in_invoice','out_refund']),('state','=','paid')])
			self.saldo = sum([purchase.amount_untaxed for purchase in purchase_ids]) + sum([round(sale.get('amount_total')) for sale in sales_ids]) - sum([customer.amount_untaxed for customer in customer_ids])

	@api.model
	def get_coin_history(self,partner_id,user_id):
		customer_ids = self.env['account.invoice'].search([('partner_id','=',partner_id),('type','in',['out_invoice','out_refund']),('state','=','paid')])
		# salesperson_ids = self.env['account.invoice'].search([('user_id','=',user_id),('type','=','out_invoice'),('state','=','paid')])
		purchase_ids = self.env['account.invoice'].search([('partner_id','=',partner_id),('type','in',['in_invoice','out_refund']),('state','=','paid')])
		sql = """SELECT l.id,l.name,l.create_date,i.amount_total,i.amount_tax from account_invoice i, account_invoice_line l, product_product p
				WHERE i.id = l.invoice_id AND p.id = l.product_id
				AND i.state = 'paid' AND i.type = 'out_invoice'
				AND p.create_uid = %s"""
		self._cr.execute(sql, (user_id,))
		sales_ids = self._cr.dictfetchall()

		vals= []

		for customer in customer_ids:
			if customer.type == 'out_invoice':
				for c in customer.invoice_line_ids:
					if c.product_id.type == 'lelang':
						data ={
							'id'   : c.id,
							'name' : 'Deposit Bid : '+c.product_id.name,
							'date' : c.create_date,
							'price': c.price_subtotal,
							'type' : 'customer'
						}
					else:
						data ={
							'id'   : c.id,
							'name' : c.product_id.name,
							'date' : c.create_date,
							'price': c.price_subtotal,
							'type' : 'customer'
						}
					vals.append(data)
			elif customer.type == 'out_refund':
				for c in customer.invoice_line_ids:
					if c.product_id.type == 'lelang':
						data ={
							'id'   : c.id,
							'name' : 'Refund Deposit : '+c.product_id.name,
							'date' : c.create_date,
							'price': c.price_subtotal,
							'type' : 'refund'
						}
						vals.append(data)

		for sale in sales_ids:
			print(sale)
			data ={
					'id'   : sale.get('id'),
					'name' : sale.get('name'),
					'date' : sale.get('create_date'),
					'price': round(sale.get('amount_total')),
					'type' : 'salesperson'
				}
			vals.append(data)
			tax_ids = self.env['account.invoice.tax'].search([('invoice_id','=',sale.get('id'))])
			for tax in tax_ids:
				data ={
						'id'   : tax.id,
						'name' : 'Tax Sales',
						'date' : tax.create_date,
						'price': round(tax.amount),
						'type' : 'tax'
					}
				vals.append(data)

		# for salesperson in salesperson_ids:
		# tax_ids = self.env['account.invoice.tax'].search([('invoice_id','=',c.id)])
		# for tax in tax_ids:
		# 		data ={
		# 			'id'   : tax.id,
		# 			'name' : 'Tax Sales',
		# 			'date' : tax.create_date,
		# 			'price': round(tax.amount),
		# 			'type' : 'tax'
		# 		}
		# 	vals.append(data)

		for purchase in purchase_ids:
			for c in purchase.invoice_line_ids:
				data ={
					'id'   : c.id,
					'name' : c.product_id.name,
					'date' : c.create_date,
					'price': c.price_subtotal,
					'type' : 'purchase'
				}
				vals.append(data)
		return vals


	# @api.model
	# def create_user(self,username,email,password,fcm_reg_ids):
	# 	return [{'id':users_id.id}]
