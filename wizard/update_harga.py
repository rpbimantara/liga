from odoo import models, fields, api

class UpdateHargaPersebaya(models.Model):
	_name = 'persebaya.update.harga'

	merchandise_id = fields.Many2one('persebaya.merchandise',string="Barang")
	harga_barang = fields.Integer(related='merchandise_id.harga_barang',string="Harga Terkini")
	harga_baru = fields.Integer(string="Harga Baru",required=True)

	@api.multi
	def update_harga(self):
		if self.harga_baru > 0:
			sql = """
				UPDATE persebaya_merchandise
				SET harga_barang = %s
				WHERE id = %s;
			"""%(str(self.harga_baru),str(self.merchandise_id.id),)
			self._cr.execute(sql)


