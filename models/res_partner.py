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

	@api.one
	def _compute_saldo(self):
		customer_ids = self.env['account.invoice'].search([('partner_id','=',self.id),('type','=','out_invoice'),('state','=','paid')])
		salesperson_ids = self.env['account.invoice'].search([('user_id','=',self.user_ids.id),('type','=','out_invoice'),('state','=','paid')])
		purchase_ids = self.env['account.invoice'].search([('partner_id','=',self.id),('type','in',['in_invoice','out_refund']),('state','=','paid')])
		self.saldo = sum([purchase.amount_untaxed for purchase in purchase_ids]) + sum([salesperson.amount_total for salesperson in salesperson_ids]) - sum([customer.amount_untaxed for customer in customer_ids])

	@api.model
	def get_coin_history(self,partner_id,user_id):
		customer_ids = self.env['account.invoice'].search([('partner_id','=',partner_id),('type','in',['out_invoice','out_refund']),('state','=','paid')])
		salesperson_ids = self.env['account.invoice'].search([('user_id','=',user_id),('type','=','out_invoice'),('state','=','paid')])
		purchase_ids = self.env['account.invoice'].search([('partner_id','=',partner_id),('type','=','in_invoice'),('state','=','paid')])
		
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

		for salesperson in salesperson_ids:
			for c in salesperson.invoice_line_ids:
				data ={
					'id'   : c.id,
					'name' : c.product_id.name,
					'date' : c.create_date,
					'price': c.price_subtotal,
					'type' : 'salesperson'
				}
				vals.append(data)
			tax_ids = self.env['account.invoice.tax'].search([('invoice_id','=',c.id)])
			for tax in tax_ids:
				data ={
					'id'   : tax.id,
					'name' : 'Tax Sales',
					'date' : tax.create_date,
					'price': round(tax.amount),
					'type' : 'tax'
				}
				vals.append(data)

		for purchase in purchase_ids:
			for c in purchase.invoice_line_ids:
				data ={
					'id'   : c.id,
					'name' : c.product_id.name,
					'date' : c.create_date,
					'price': c.price_unit,
					'type' : 'purchase'
				}
				vals.append(data)

		return vals