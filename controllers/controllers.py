# -*- coding: utf-8 -*-
from odoo import http

# class Persebaya(http.Controller):
#     @http.route('/persebaya/persebaya/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/persebaya/persebaya/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('persebaya.listing', {
#             'root': '/persebaya/persebaya',
#             'objects': http.request.env['persebaya.persebaya'].search([]),
#         })

#     @http.route('/persebaya/persebaya/objects/<model("persebaya.persebaya"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('persebaya.object', {
#             'object': obj
#         })