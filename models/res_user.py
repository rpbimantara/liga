from odoo import fields, models,api

class ResUsersInherit(models.Model):
	_inherit = 'res.users'

	club_id = fields.Many2one('persebaya.club', string="Club")
	fcm_reg_ids = fields.Char(string="Reg. Id")
	
	@api.multi
	def preference_change_profile(self):
		return {
				'name':'Profile',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'res.partner',
				'type': 'ir.actions.act_window',
				'domain': [('id', '=', self.env.user.partner_id.id)],
				}



