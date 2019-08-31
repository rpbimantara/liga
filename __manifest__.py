# -*- coding: utf-8 -*-
{
    'name': "persebaya",

    'summary': """
        #KITAPERSEBAYA""",

    'description': """
        Ini adalah Modul yang di kembangkan untuk kebutuhan skripsi berjudul Sistem Manajemen Fans Persebaya
    """,

    'author': "Ruli Putra Bimantara",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','hr','event','sale','purchase','account_accountant'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        # 'security/ir.model.access.csv',
        'wizard/top_up_view.xml',
        'views/lelang_view.xml',
        'views/club_view.xml',
        'views/stadion_view.xml',
        'views/jadwal_view.xml',
        'views/liga_view.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'views/hr_employee.xml',
        'views/berita_view.xml',
        'views/berita_kategori_view.xml',
        'views/event_inherits.xml',
        'views/product_template.xml',
        'views/security.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}