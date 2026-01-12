# -*- coding: utf-8 -*-

from odoo import fields, models

class HrBenefitRule(models.Model):
    _name = "tt.hr.benefit.rule"
    _description = "Regla de Beneficio por Tipo de Contrato"
    _order = "contract_type_id, benefit_code, id"

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        required=True,
    )

    contract_type_id = fields.Many2one(
        "hr.contract.type",
        string="Tipo de contrato",
        required=True,
        ondelete="restrict",
    )

    benefit_code = fields.Selection(
        [
            ("vacation", "Vacaciones"),
            ("severance", "Prestaciones"),
            ("bonus", "Bono"),
            ("other", "Otro"),
        ],
        required=True,
        string="Beneficio",
    )

    amount_type = fields.Selection(
        [("fixed", "Monto fijo"), ("percent", "Porcentaje del salario")],
        required=True,
        default="fixed",
        string="Tipo de cálculo",
    )

    amount = fields.Float(string="Monto / %", required=True, default=0.0)
    note = fields.Char(string="Descripción")
