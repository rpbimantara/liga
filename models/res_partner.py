from odoo import fields, models

class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	nik = fields.Char(string="NIK",required=True)
	tgl_lahir = fields.Date(string="Birthday")
	jeniskelamin = fields.Selection([
		('Man', 'Man'),
		('Woman', 'Woman'),
	], string="Gender", default='Man')
	saldo = fields.Integer(string="Coin",readonly=True)
	komunitas = fields.Char(string="Community")

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

	# def _default_receivable(self):
	# 	return self.env['account.account'].search([('code', '=', "1")], limit=1).id


	# def _default_payable(self):
	# 	return self.env['account.account'].search([('code', '=', "2")], limit=1).id