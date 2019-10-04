
from ast import literal_eval

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr
from odoo.addons.auth_signup.models.res_partner import SignupError, now

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
				
	@api.model
	def create_user(self,username,email,password,reg_id):
		result = ''
		values = {
			'login':username,
			'name':username,
			'email':email,
			'password':password,
			'fcm_reg_ids':reg_id
		}
		result = str(self._create_user_from_template(values))
		# partner_id = self.env['res.partner'].create({
		# 			'name':username,
		# 			'email':email,
		# })
		# cek_user = self.env['res.users'].search([('login','=',username),('partner_id','=',partner_id.id)])
		# if not cek_user:
		# 	sql = """
		# 		INSERT INTO res_users (login,partner_id,club_id,password,fcm_reg_ids,company_id) 
		# 			values ('%s','%s','%s','%s','%s','%s')
		# 	"""%(str(username),str(partner_id.id),str(52),str(password),reg_id,str(1),)
		# 	self._cr.execute(sql)
		# 	user = self.env['res.users'].search(['partner_id','=',partner_id.id])
		# 	user.write({
        #         'groups_id': [
        #             (6, 0, [self.env.ref('persebaya.group_fans').id]),
		# 			(6, 0, [self.env.ref('sales_team.group_sale_salesman').id]),
		# 			(6, 0, [self.env.ref('event.group_event_user').id])
        #         ]})
		# 	# self.env['res.users'].create({
		# 	# 	'login':username,
		# 	# 	'partner_id':partner_id.id,
		# 	# 	'club_id':52,
		# 	# 	'password':password,
		# 	# 	'fcm_reg_ids':reg_id,
		# 	# 	'company_id':1,
		# 	# })
		# 	result = 'baru'
		# else:
		# 	result = 'sudah ada'
		return [{'name':result}]


	def _create_user_from_template(self, values):
		# template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id', 'False'))
		# print(template_user_id)
		template_user = self.browse(3)
		print(template_user)
		if not template_user.exists():
			raise ValueError(_('Signup: invalid template user'))

		if not values.get('login'):
			raise ValueError(_('Signup: no login given for new user'))
		if not values.get('partner_id') and not values.get('name'):
			raise ValueError(_('Signup: no name or partner given for new user'))

        # create a copy of the template user (attached to a specific partner_id if given)
		values['active'] = True
		values['customer'] = True
		try:
			with self.env.cr.savepoint():
				return template_user.with_context(no_reset_password=True).copy(values)
		except Exception as e:
            # copy may failed if asked login is not available.
			# print(e)
			raise e