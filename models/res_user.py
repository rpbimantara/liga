# -*- coding: utf-8 -*-

from ast import literal_eval
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import ustr
from odoo.addons.auth_signup.models.res_partner import SignupError, now
_logger = logging.getLogger(__name__)

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
		counter = 1
		if counter == 1:
			result = str(self.sudo()._create_user_from_template(values))
			counter += 1
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

	@api.model
	def reset_password_users(self, login):
		""" retrieve the user corresponding to login (login or email),
			and reset their password
		"""

		users = self.env['res.users'].search([('login', '=', login)])
		if not users:
			users = self.env['res.users'].search([('email', '=', login)])
		if len(users) != 1:
			raise Exception(_('Reset password: invalid username or email'))
		
		# reset = users.sudo()._action_reset_password()
		template = self.env.ref('auth_signup.reset_password_email')
		template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
		template.sudo().write(template_values)
		template.with_context(lang=users.lang).sudo().send_mail(users.id, force_send=True, raise_exception=True)

		return [{'name':template.id}]

	@api.multi
	def _action_reset_password(self):
		""" create signup token for each user, and send their signup url by email """
		# prepare reset password signup
		create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
		expiration = False if create_mode else now(days=+1)

		self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
		template = False
		if create_mode:
			try:
				template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
			except ValueError:
				pass
		if not template:
			template = self.env.ref('auth_signup.reset_password_email')
		assert template._name == 'mail.template'

		template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
		template.write(template_values)

		for user in self:
			if not user.email:
				raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
			with self.env.cr.savepoint():
				template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
			_logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
		return template