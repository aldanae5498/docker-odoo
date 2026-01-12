# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountDiscountRule(models.Model):
    _name = "account.discount.rule"
    _description = "Regla de descuento por tipo de cliente"
    _order = "customer_type"

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(default=True)

    customer_type = fields.Selection(
        [
            ("minorista", "Minorista"),
            ("mayorista", "Mayorista"),
            ("vip", "VIP"),
        ],
        required=True,
        string="Tipo de cliente",
    )

    discount_percent = fields.Float(
        string="Descuento (%)",
        required=True,
        help="Porcentaje de descuento a aplicar en las líneas de factura",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.company,
    )
