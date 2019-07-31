from odoo import api, fields, models

class ProductTemplateInherits(models.Model):
	_inherit = "product.template"

	variant_text = fields.Text(String="Variant")


class ProductProductInherits(models.Model):
	_inherit = "product.product"

	variant_text = fields.Text(String="Variant", compute='_compute_variant_text')


	@api.depends('attribute_line_ids')
	def _compute_variant_text(self):
		for s in self:
			text_string = ""
			# if len(s.attribute_value_ids) > 0 :
			for a in s.attribute_value_ids:
				text_string += a.name +", "
			text_string = text_string.rstrip(', ')
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
				'image' : product.image_medium,
				'variant' : variant_text,
				'qty_available' : product.qty_available,
				'desc' : product.description_sale
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
				'harga'	: order.price_unit,
				'qty'	: order.product_uom_qty,
				'image'	: order.product_id.image_medium,
				'stock' : order.product_id.qty_available
			}
			vals.append(data)
		return vals
