from odoo import fields, models, api
from datetime import datetime, timedelta
import barcode
from barcode import generate
from barcode.writer import ImageWriter
from StringIO import StringIO
import base64
import os


class EventEventInherit(models.Model):
	_inherit = 'event.event'


	jadwal_id = fields.Many2one('persebaya.jadwal', string="Match Schedule")
	image = fields.Binary(string="Poster")




class EventRegistrationBarcode(models.Model):
	_inherit = 'event.registration'


	barcode = fields.Char(String="Barcode",readonly=True)
	barcode_image = fields.Binary(String ="Barcode Image",readonly=True)


	@api.model
	def create(self, vals):
		res = super(EventRegistrationBarcode, self).create(vals)
		change_date = datetime.strptime(res.date_open, '%Y-%m-%d %H:%M:%S') +  timedelta(hours=7)
		date = change_date.strftime("%Y%m%d%H%M%S")
		res.barcode = str(res.partner_id.id)+str(res.event_id.id)+date+str(res.id)
		ean = barcode.get('ean13', res.barcode, writer=ImageWriter())
		fullname = ean.save('/tmp/' + res.barcode)
		with open(fullname, 'rb') as f:
			file = f.read()
		res.barcode_image = base64.b64encode(file)
		os.remove(fullname)
		return res

	@api.model
	def search_ticket(self,partner_id):
		vals = []
		registration_ids = self.env['event.registration'].sudo().search([('partner_id','=',partner_id),('state','=','open')])
		print(registration_ids)
		for registration_id in registration_ids:
			data = {
				'id':registration_id.id,
				'name':registration_id.name,
				'date_open':registration_id.date_open,
				'event_id':registration_id.event_id.name,
				'event_ticket_id':registration_id.event_ticket_id.name,
				'barcode_image':registration_id.barcode_image
			}
			print(data)
			vals.append(data)
		return vals

		