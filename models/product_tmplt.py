from odoo import api, fields, models

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
		('jalan', 'On Progress'),
		('selesai', 'End'),
	], string="State", default='jalan', readonly=True)
	status_donasi = fields.Selection([
		('draft', 'Draft'),
		('jalan', 'On Progress'),
		('selesai', 'End'),
	], string="State", default='draft', readonly=True)

	# @api.onchange('status_lelang')
	# def _onchange_status_lelang(self):
	# 	if self.status_lelang == 'selesai' and self.pemenang:
			


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
	_inherit = "sale.order.line"

	@api.model
	def get_checkout_list(self,partner_id):
		order_id = self.env['sale.order'].search([('partner_id','=',partner_id),('state','=','draft')]).id
		order_ids = self.env['sale.order.line'].search([('order_id','=',order_id)])
		vals = []
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
		print(vals)
		return vals


class DonasiPersebaya(models.Model):
	_name = 'persebaya.donasi'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	product_id = fields.Many2one('product.template',string="Product")
	user_bid = fields.Many2one('res.users',string="Participant")
	nilai = fields.Integer(string="Nominal",required=True)
	keterang = fields.Char(string="Note")