from odoo import models, fields, api

class UpdateStockPersebaya(models.Model):
	_name = 'persebaya.update.stock'

	merchandise_id = fields.Many2one('persebaya.merchandise',string="Barang",required=True)
	ukuran_id = fields.Many2one('persebaya.merchandise.line',string="Ukuran",required=True)
	stock_ukuran = fields.Integer(related='ukuran_id.stock_ukuran',string="Stock Terkini",readonly=True)
	update_stock = fields.Integer(string="Stock Tambahan",required=True)

	@api.multi
	def tambah_stock(self):
		if self.update_stock > 0:
			sql = """
				UPDATE persebaya_merchandise_line
				SET stock_ukuran = %s
				WHERE merchandise_id = %s AND id = %s;
			"""%(str(self.update_stock),str(self.merchandise_id.id),str(self.ukuran_id.id),)
			self._cr.execute(sql)
