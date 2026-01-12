# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_type = fields.Selection(
        [
            ("minorista", "Minorista"),
            ("mayorista", "Mayorista"),
            ("vip", "VIP"),
        ],
        string="Tipo de cliente",
        tracking=True,
    )