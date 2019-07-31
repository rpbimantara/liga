from odoo import fields, models,api

class ResCompanyInherit(models.Model):
	_inherit = 'res.company'


	api_key = fields.Text('Api Key')
	club_id = fields.Many2one('persebaya.club', string="Club")
